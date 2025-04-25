from django.core.exceptions import ValidationError
from django.db.models import Count, Q
from django.contrib.postgres.aggregates import ArrayAgg
from django.apps import apps
from collections import defaultdict
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from projects.models import Member, MemberAttributeDescription, Project
from projects.permissions import IsProjectAdmin, IsAnnotationApprover

class ReportingView(APIView):
    permission_classes = [IsAuthenticated & (IsProjectAdmin | IsAnnotationApprover)]

    def get(self, request, project_id):
        try:
            members = [int(m) for m in request.GET.getlist('members', [])]
            perspective_attributes = request.GET.getlist('attributes', [])
            descriptions = request.GET.getlist('descriptions', [])
            labels = request.GET.getlist('labels', [])
            
            project = Project.objects.get(pk=project_id)
            
            # Get relevant members
            members_qs = Member.objects.filter(project=project)
            if members:
                members_qs = members_qs.filter(id__in=members)
            
            # Get member attribute descriptions
            query = Q(attribute__perspective__projects=project_id)
            if members:
                query &= Q(member_id__in=members)
            if perspective_attributes:
                query &= Q(attribute__name__in=perspective_attributes)
            
            member_descriptions = MemberAttributeDescription.objects.filter(query)\
                .select_related('attribute', 'member__user')\
                .prefetch_related('attribute__options')

            # 1. Calculate conflict statistics
            examples = project.examples.annotate(
                num_annotators=Count('states__confirmed_by', distinct=True)
            ).filter(num_annotators__gt=1).prefetch_related('states__confirmed_by')
            
            total_examples = examples.count()
            conflict_count = 0
            
            for example in examples:
                states = example.states.all()
                annotations = []
                for state in states:
                    # Extract annotations from labels (e.g., categories, spans)
                    Category = apps.get_model('labels', 'Category')
                    categories = Category.objects.filter(
                        example=state.example,
                        user=state.confirmed_by
                    ).values_list('label__text', flat=True)
                    annotations.append(sorted(categories))
                
                if len(set(map(str, annotations))) > 1:
                    conflict_count += 1

            # 2. Calculate attribute distributions
            attribute_distributions = defaultdict(lambda: defaultdict(int))
            
            for member in members_qs:
                attributes = {
                    desc.attribute.name: desc.description
                    for desc in member_descriptions.filter(member=member)
                    if not perspective_attributes or desc.attribute.name in perspective_attributes
                }
                
                for attr_name, attr_value in attributes.items():
                    attribute_distributions[attr_name][attr_value] += 1

            # Format attribute distributions
            formatted_distributions = []
            for attr_name, values in attribute_distributions.items():
                total = sum(values.values())
                formatted_distributions.append({
                    'attribute': attr_name,
                    'total_members': total,
                    'data': [{
                        'value': value, 
                        'count': count
                    } for value, count in values.items()]
                })

            label_distributions = []
            if perspective_attributes and descriptions and labels:
                desc_query = Q(attribute__name__in=perspective_attributes) & Q(description__in=descriptions)
                
                # Get grouped attribute descriptions
                grouped_descriptions = MemberAttributeDescription.objects.filter(desc_query)\
                    .values('attribute__name', 'description')\
                    .annotate(
                        total_members=Count('member', distinct=True),
                        user_ids=ArrayAgg('member__user_id', distinct=True)
                    )
                
                # Process each attribute-description group
                for group in grouped_descriptions:
                    attr_name = group['attribute__name']
                    desc_text = group['description']
                    user_ids = group['user_ids']
                    total_members = group['total_members']

                    # Get per-example label counts
                    label_counts = Category.objects.filter(
                        example__project=project,
                        user_id__in=user_ids,
                        label__text__in=labels
                    ).values('example__id', 'example__text', 'label__text') \
                    .annotate(count=Count('id'))
                    
                    # Group by example
                    examples = defaultdict(lambda: {'labels': [], 'total': 0})
                    for item in label_counts:
                        ex = examples[item['example__id']]
                        ex['example_id'] = item['example__id']
                        ex['example_text'] = item['example__text']
                        ex['labels'].append({
                            'label': item['label__text'],
                            'count': item['count']
                        })
                        ex['total'] += item['count']
                    
                    # Add to distributions
                    label_distributions.append({
                        'attribute': attr_name,
                        'description': desc_text,
                        'total_members': total_members,
                        'examples': list(examples.values())
                    })

            response_data = {
                'total_examples': total_examples,
                'conflict_count': conflict_count,
                'attribute_distributions': formatted_distributions,
                'label_distributions': label_distributions
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
        
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Project.DoesNotExist:
            return Response({'error': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)