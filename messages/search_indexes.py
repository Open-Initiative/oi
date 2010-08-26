from haystack import indexes, site
from oi.messages.models import Message

class MessageIndex(indexes.RealTimeSearchIndex):
    text = indexes.CharField(document=True, use_template=True)
    title = indexes.CharField(model_attr='title')
    author = indexes.CharField(model_attr='author', null=True)
    created = indexes.DateTimeField(model_attr='created')
    modified = indexes.DateTimeField(model_attr='modified')
    category = indexes.BooleanField(model_attr='category')

site.register(Message, MessageIndex)
