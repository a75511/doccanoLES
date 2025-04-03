from django.db.models import Count, Manager


class ExampleManager(Manager):
    def bulk_create(self, objs, batch_size=None, ignore_conflicts=False):
        super().bulk_create(objs, batch_size=batch_size, ignore_conflicts=ignore_conflicts)
        uuids = [data.uuid for data in objs]
        examples = self.in_bulk(uuids, field_name="uuid")
        return [examples[uid] for uid in uuids]


class ExampleStateManager(Manager):
    def count_done(self, examples, user=None):
        if user:
            queryset = self.filter(example_id__in=examples, confirmed_by=user)
        else:
            queryset = self.filter(example_id__in=examples)
        return queryset.distinct().values("example").count()

    def measure_member_progress(self, examples, members):
        done_count = (
            self.filter(example_id__in=examples).values("confirmed_by__username").annotate(total=Count("confirmed_by"))
        )
        response = {
            "total": examples.count(),
            "progress": [{"user": obj["confirmed_by__username"], "done": obj["total"]} for obj in done_count],
        }
        members_with_progress = {o["confirmed_by__username"] for o in done_count}
        for member in members:
            if member.username not in members_with_progress:
                response["progress"].append({"user": member.username, "done": 0})
        return response
    
    def reset_confirmation(self, project):
        self.filter(example__project=project).delete()
    
    def check_for_disagreements(self, example):
        from .models import Disagreement
        
        # Get all states for this example
        states = self.filter(example=example).select_related('confirmed_by')
        
        # If there are less than 2 annotations, no disagreement possible
        if states.count() < 2:
            return None
        
        # Check if all states have the same annotation (you'll need to define what constitutes agreement)
        # For now, we'll assume we have a method to compare annotations
        first_state = states.first()
        disagreements = []
        
        for state in states[1:]:
            if not self._annotations_agree(first_state, state):
                # Found a disagreement
                disagreement, created = Disagreement.objects.get_or_create(
                    example=example,
                    defaults={'resolved': False}
                )
                disagreement.users.add(first_state.confirmed_by, state.confirmed_by)
                disagreements.append(disagreement)
        
        return disagreements if disagreements else None
    
    def _annotations_agree(self, state1, state2):
        """
        Compare two ExampleStates to see if they agree.
        This is a placeholder - you'll need to implement actual comparison logic
        based on your annotation data structure.
        """
        # For now, we'll just compare the meta field as a simple example
        return state1.example.meta == state2.example.meta