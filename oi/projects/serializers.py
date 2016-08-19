from pyld import jsonld
from rest_framework import serializers, fields, renderers, parsers
from oi.projects.models import Project

class JSONLDRenderer(renderers.JSONRenderer):
    media_type = 'application/ld+json'
    def render(self, data, accepted_media_type=None, renderer_context=None):
        if data.has_key('@id'): #no context for OPTIONS requests
            data["@context"] = "http://owl.openinitiative.com/oicontext.jsonld"
        return super(JSONLDRenderer, self).render(jsonld.expand(data), accepted_media_type, renderer_context)

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
    tasks = LDPField(many=True, prefix="http://localhost:8000/project/ldpcontainer/")
    messages = LDPField(many=True, prefix="http://localhost:8000/project/ldpcontainer/")
    specs = LDPField(many=True, prefix="http://localhost:8000/project/ldpcontainer/")
    author = LDPField(prefix="http://localhost:8000/user/ldpcontainer/")
    
    def __init__(self, *args, **kwargs):
        super(ProjectSerializer, self).__init__(*args, **kwargs)
        self.base_fields['@id'] = IdField(source="id")
    
    class Meta:
        model = Project
        fields = ('@id', 'title', 'author', 'state', 'tasks', 'spec_set', 'message_set')
