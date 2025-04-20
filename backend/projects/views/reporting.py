from itertools import combinations
from django.http import HttpResponse
import json
from django.core.exceptions import ValidationError
from django.db.models import Count
from examples.models import Example
from projects.services.reporting import ReportService

def disagreement_statistics(request, project_id):
    try:
        members = [int(m) for m in request.GET.getlist('members', [])]
        perspective_attributes = request.GET.getlist('attributes', [])
        
        service = ReportService()
        stats = service.get_disagreement_stats(
            project_id=project_id,
            members=members,
            perspective_attributes=perspective_attributes
        )

        # Calculate attribute breakdown
        attribute_breakdown = []
        for attr in perspective_attributes:
            attr_examples = Example.objects.filter(
                project_id=project_id,
                meta__has_key=attr
            ).annotate(num_states=Count('states')).filter(num_states__gt=1)
            
            total = attr_examples.count()
            conflict_count = sum(1 for e in attr_examples if e.states.count() > 1 and 
                               any(s1.annotations != s2.annotations 
                                   for s1, s2 in combinations(e.states.all(), 2)))
            
            attribute_breakdown.append({
                'attribute': attr,
                'conflictCount': conflict_count,
                'totalExamples': total
            })

        response_data = {
            'total_examples': stats['total_examples'],
            'conflict_percentage': stats['conflict_percentage'],
            'agreement_percentage': 100 - stats['conflict_percentage'],
            'attribute_distributions': stats['attribute_distributions'] 
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