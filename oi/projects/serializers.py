from pyld import jsonld
from rest_framework import serializers, fields, renderers, parsers
from django.conf import settings
from oi.projects.models import Project
domain = dict(settings.OI_DOMAINS)['Open Initiative Projects']

class JSONLDRenderer(renderers.JSONRenderer):
    media_type = 'application/ld+json'
    def render(self, data, accepted_media_type=None, renderer_context=None):
        data["@context"] = "http://owl.openinitiative.com/oicontext.jsonld"
        return super(JSONLDRenderer, self).render(data, accepted_media_type, renderer_context)

class JSONLDParser(parsers.JSONParser):
    media_type = 'application/ld+json'
    def parse(self, stream, media_type=None, parser_context=None):
        data = super(JSONLDParser, self).parse(stream, media_type, parser_context)
        return jsonld.compact(data['@graph'], data['@context'])

class LDPField(serializers.RelatedField):
    def __init__(self, *args, **kwargs):
        self.prefix = kwargs.pop("prefix", "")
        super(LDPField, self).__init__(*args, **kwargs)
    
    def to_native(self, instance):
        return {"@id": "%s%s"%(self.prefix, instance.pk) }
    def from_native(self, instance):
        return super(LDPField, self).from_native(instance["@id"].replace(self.prefix, ""))

class IdField(serializers.CharField):
    def to_native(self, value):
        return "%s"%value
    def from_native(self, instance):
        return super(IdField, self).from_native(instance.split("/")[-1])

class ProjectSerializer(serializers.ModelSerializer):
    descendants = LDPField(many=True, prefix="http://%s/project/ldpcontainer/"%domain)
    message_set = LDPField(many=True, prefix="http://%s/project/ldpcontainer/"%domain)
    spec_set = LDPField(many=True, prefix="http://%s/project/ldpcontainer/"%domain)
    author = LDPField(prefix="http://%s/user/ldpcontainer/"%domain)
    state = IdField()
    
    def __init__(self, *args, **kwargs):
        super(ProjectSerializer, self).__init__(*args, **kwargs)
        self.base_fields['@id'] = IdField(source="id")
        self.base_fields['ldp:contains'] = LDPField(many=True, source="tasks", prefix="http://%s/project/ldpcontainer/"%domain)
    
    class Meta:
        model = Project
        fields = ('@id', 'title', 'author', 'state', 'ldp:contains', 'descendants', 'spec_set', 'message_set')
