from itertools import combinations
from django.http import HttpResponse
import json
from django.core.exceptions import ValidationError
from django.db.models import Count, Q
from django.apps import apps
from collections import defaultdict
from examples.models import Example
from projects.models import Member, MemberAttributeDescription, Project
from rest_framework.permissions import IsAuthenticated
from projects.permissions import IsProjectAdmin, IsAnnotationApprover

def disagreement_statistics(request, project_id):
    permission_classes = [IsAuthenticated & (IsProjectAdmin | IsAnnotationApprover)]
    
    try:
        members = [int(m) for m in request.GET.getlist('members', [])]
        perspective_attributes = request.GET.getlist('attributes', [])
        
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

        response_data = {
            'total_examples': total_examples,
            'conflict_count': conflict_count,
            'attribute_distributions': formatted_distributions
        }
        
        return HttpResponse(
            json.dumps(response_data),
            content_type='application/json'
        )
    
    except ValidationError as e:
        return HttpResponse(
            json.dumps({'error': str(e)}),
            status=400,
            content_type='application/json'
        )
    except Exception as e:
        return HttpResponse(
            json.dumps({'error': str(e)}),
            status=500,
            content_type='application/json'
        )