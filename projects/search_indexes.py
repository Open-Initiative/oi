from haystack import indexes, site
from oi.projects.models import Project

class ProjectIndex(indexes.RealTimeSearchIndex):
    text = indexes.CharField(document=True, use_template=True)
    title = indexes.CharField(model_attr='title')
    author = indexes.CharField(model_attr='author', null=True)
    assignee = indexes.CharField(model_attr='assignee', null=True)
    offer = indexes.FloatField(model_attr='offer')
    created = indexes.DateTimeField(model_attr='created')
    modified = indexes.DateTimeField(model_attr='modified')
    start_date = indexes.DateTimeField(model_attr='start_date')
    due_date = indexes.DateTimeField(model_attr='due_date')
    
site.register(Project, ProjectIndex)
