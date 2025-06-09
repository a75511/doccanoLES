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
from examples.models import Example

class ReportingView(APIView):
    permission_classes = [IsAuthenticated & (IsProjectAdmin | IsAnnotationApprover)]

    def get(self, request, project_id):
        try:
            perspective_attributes = request.GET.getlist('attributes', [])
            descriptions = request.GET.getlist('descriptions', [])
            view_type = request.GET.get('view', 'all')  # 'all', 'agreement', 'disagreement'
            
            project = Project.objects.get(pk=project_id)
            members_qs = Member.objects.filter(project=project)
            total_members = members_qs.count()

            # Get examples with multiple annotations
            examples = project.examples.annotate(
                num_annotators=Count('states__confirmed_by', distinct=True)
            ).filter(num_annotators__gt=1)

            total_examples = examples.distinct().count()
            conflict_count = 0
            
            # Conflict detection remains the same
            for example in examples:
                states = example.states.all()
                annotations = []
                for state in states:
                    # Get member through user relationship
                    try:
                        member = Member.objects.get(project=project, user=state.confirmed_by)
                        Category = apps.get_model('labels', 'Category')
                        categories = Category.objects.filter(
                            example=state.example,
                            user=state.confirmed_by
                        ).values_list('label__text', flat=True)
                        annotations.append(sorted(categories))
                    except Member.DoesNotExist:
                        continue
                
                if len(set(map(str, annotations))) > 1:
                    conflict_count += 1

            label_distributions = []
            if perspective_attributes:
                # Build OR query for selected attributes and descriptions
                attribute_query = Q()
                for attr in perspective_attributes:
                    if descriptions:
                        # OR between descriptions for same attribute
                        desc_query = Q()
                        for desc in descriptions:
                            desc_query |= Q(description=desc)
                        attribute_query |= Q(attribute__name=attr) & desc_query
                    else:
                        attribute_query |= Q(attribute__name=attr)

                # Get all matching member descriptions
                member_descriptions = MemberAttributeDescription.objects.filter(
                    Q(attribute__perspective__projects=project_id) & attribute_query
                ).select_related('member', 'attribute')

                # Create member ID set
                member_ids = set()
                member_attr_map = defaultdict(lambda: defaultdict(list))
                for md in member_descriptions:
                    member_ids.add(md.member_id)
                    member_attr_map[md.member_id][md.attribute.name].append(md.description)

                total_group_members = len(member_ids)
                
                # Get users through members
                users = Member.objects.filter(
                    id__in=member_ids
                ).values_list('user', flat=True)

                if not users:
                    # No members match the filter
                    label_distributions = []
                else:
                    # Get annotations
                    label_counts = Category.objects.filter(
                        example__project=project,
                        user__in=users
                    ).values('example_id', 'example__text', 'label__text') \
                    .annotate(count=Count('id'))

                    # Get assigned examples through members
                    assigned_examples = Example.objects.filter(
                        project=project,
                        assignments__assignee__in=member_ids
                    ).distinct()

                    # Build example structure
                    example_map = {}
                    for example in assigned_examples:
                        example_map[example.id] = {
                            'example_id': example.id,
                            'example_text': example.text,
                            'labels': defaultdict(int),
                            'annotated_members': set(),
                            'total_possible': total_group_members,
                            'max_label_count': 0,
                            'agreement_rate': 0.0
                        }

                    # Populate annotation data
                    for ann in label_counts:
                        ex_id = ann['example_id']
                        if ex_id in example_map:
                            example = example_map[ex_id]
                            example['labels'][ann['label__text']] += ann['count']
                            # Track max count for agreement calculation
                            if ann['count'] > example['max_label_count']:
                                example['max_label_count'] = ann['count']
                            
                            # Track member annotations
                            annotators = Category.objects.filter(
                                example_id=ex_id,
                                label__text=ann['label__text'],
                                user__in=users
                            ).values_list('user', flat=True).distinct()
                            
                            # Convert to member IDs
                            member_annotators = Member.objects.filter(
                                user__in=annotators,
                                project=project
                            ).values_list('id', flat=True)
                            
                            example['annotated_members'].update(member_annotators)

                    # Calculate agreement rate and filter by view type
                    formatted_examples = []
                    for ex_id, ex in example_map.items():
                        total_annotated = len(ex['annotated_members'])
                        non_annotated = ex['total_possible'] - total_annotated
                        
                        # Calculate agreement rate
                        if total_annotated > 0:
                            agreement_rate = (ex['max_label_count'] / total_annotated) * 100
                        else:
                            agreement_rate = 0.0
                            
                        ex['agreement_rate'] = agreement_rate
                        ex['non_annotated'] = non_annotated
                        
                        # Apply view filter
                        if view_type == 'all' or \
                           (view_type == 'agreement' and agreement_rate >= 60) or \
                           (view_type == 'disagreement' and agreement_rate < 60):
                            labels = [{'label': k, 'count': v} for k, v in ex['labels'].items()]
                            formatted_examples.append({
                                'example_id': ex['example_id'],
                                'example_text': ex['example_text'],
                                'labels': labels,
                                'total': total_annotated,
                                'non_annotated': non_annotated,
                                'agreement_rate': agreement_rate,
                                'is_agreement': agreement_rate >= 60
                            })

                    label_distributions.append({
                        'attributes': perspective_attributes,
                        'descriptions': descriptions,
                        'total_members': total_group_members,
                        'examples': formatted_examples
                    })

            response_data = {
                'total_examples': total_examples,
                'conflict_count': conflict_count,
                'total_members': total_members,
                'label_distributions': label_distributions
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
        
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Project.DoesNotExist:
            return Response({'error': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)