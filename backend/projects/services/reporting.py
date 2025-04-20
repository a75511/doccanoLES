from django.db.models import Count, Q
from django.apps import apps
from collections import defaultdict
from projects.models import Member, MemberAttributeDescription, Project
from rest_framework.permissions import IsAuthenticated
from projects.permissions import IsProjectAdmin,IsAnnotationApprover

class ReportService:
    permission_classes= [IsAuthenticated & (IsProjectAdmin | IsAnnotationApprover)]
    def get_disagreement_stats(self, project_id: int, members: list[int] = None,
                              perspective_attributes: list[str] = None):
        project = Project.objects.get(pk=project_id)
        
        # Get relevant members
        members_qs = Member.objects.filter(project=project)
        if members:
            members_qs = members_qs.filter(id__in=members)
        
        # Get member attribute descriptions
        member_descriptions = self._get_member_descriptions(
            project_id, 
            members,
            perspective_attributes
        )

        # 1. Calculate conflict statistics (original functionality)
        examples = project.examples.annotate(
            num_annotators=Count('states__confirmed_by', distinct=True)
        ).filter(num_annotators__gt=1).prefetch_related('states__confirmed_by')
        
        total_examples = examples.count()
        conflict_count = 0
        
        for example in examples:
            states = example.states.all()
            annotations = [self._get_annotations(state) for state in states]
            if len(set(map(str, annotations))) > 1:
                conflict_count += 1

        # 2. Calculate attribute distributions (new functionality)
        attribute_distributions = defaultdict(lambda: defaultdict(int))
        
        for member in members_qs:
            attributes = {
                desc.attribute.name: desc.description
                for desc in member_descriptions.filter(member=member)
                if not perspective_attributes or desc.attribute.name in perspective_attributes
            }
            
            for attr_name, attr_value in attributes.items():
                attribute_distributions[attr_name][attr_value] += 1

        # Format response
        formatted_distributions = []
        for attr_name, values in attribute_distributions.items():
            total = sum(values.values())
            formatted_distributions.append({
                'attribute': attr_name,
                'total_members': total,
                'data': [{
                    'value': value, 
                    'count': count,
                    'percentage': (count / total * 100) if total > 0 else 0
                } for value, count in values.items()]
            })

        return {
            'total_examples': total_examples,
            'conflict_percentage': (conflict_count / total_examples * 100) if total_examples > 0 else 0,
            'attribute_distributions': formatted_distributions
        }
    def _get_member_descriptions(self, project_id, members, attributes):
        query = Q(attribute__perspective__projects=project_id)
        if members:
            query &= Q(member_id__in=members)
        if attributes:
            query &= Q(attribute__name__in=attributes)
        
        return MemberAttributeDescription.objects.filter(query)\
            .select_related('attribute', 'member__user')\
            .prefetch_related('attribute__options')
    
    def _get_annotations(self, state):
        """Extract annotations from labels (e.g., categories, spans)"""
        # Example: Fetch categories for text classification
        Category = apps.get_model('labels', 'Category')
        categories = Category.objects.filter(
            example=state.example,
            user=state.confirmed_by
        ).values_list('label__text', flat=True)
        return sorted(categories)