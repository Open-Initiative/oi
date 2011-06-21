from haystack import indexes, site
from oi.projects.models import Project
from oi.messages.models import OI_READ

class ProjectIndex(indexes.RealTimeSearchIndex):
    text = indexes.CharField(document=True, use_template=True)
    title = indexes.CharField(model_attr='title')
    author = indexes.CharField(model_attr='author', null=True)
    assignee = indexes.CharField(model_attr='assignee', null=True)
    offer = indexes.FloatField(model_attr='offer')
    created = indexes.DateTimeField(model_attr='created')
    modified = indexes.DateTimeField(model_attr='modified')
    start_date = indexes.DateTimeField(model_attr='start_date', null=True)
    due_date = indexes.DateTimeField(model_attr='due_date', null=True)
    public = indexes.BooleanField(model_attr='public')
    perms = indexes.MultiValueField()
    
    def prepare_perms(self, obj):
        # Since we're using a M2M relationship with a complex lookup,
        # we can prepare the list here.
        return [perm.user for perm in obj.projectacl_set.filter(permission=OI_READ)]
    
site.register(Project, ProjectIndex)
