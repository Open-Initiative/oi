from haystack import indexes, site
from oi.messages.models import Message, OI_READ

class MessageIndex(indexes.RealTimeSearchIndex):
    text = indexes.CharField(document=True, use_template=True)
    title = indexes.CharField(model_attr='title')
    author = indexes.CharField(model_attr='author', null=True)
    created = indexes.DateTimeField(model_attr='created')
    modified = indexes.DateTimeField(model_attr='modified')
    category = indexes.BooleanField(model_attr='category')
    public = indexes.BooleanField(model_attr='public')
    perms = indexes.MultiValueField()
    
    def prepare_perms(self, obj):
        # Since we're using a M2M relationship with a complex lookup,
        # we can prepare the list here.
        return [perm.user for perm in obj.messageacl_set.filter(permission=OI_READ)]

site.register(Message, MessageIndex)
