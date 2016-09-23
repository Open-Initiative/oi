from pyld import jsonld
from rest_framework import serializers, fields, renderers, parsers
from django.conf import settings
from oi.projects.models import Project, Release
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
        iri = "http://%s/project/ldpcontainer/%s"%(domain, parser_context["kwargs"]["pk"])
        for obj in jsonld.frame(data['@graph'], data['@context'])['@graph']:
            if obj.get("@id") =='./':
                del obj["@id"]
                return obj
            if obj.get("@id") == iri:
                return obj

class LDPField(serializers.RelatedField):
    def __init__(self, *args, **kwargs):
        self.prefix = kwargs.pop("prefix", "")
        self.fields = kwargs.pop("fields", [])
        self.model = kwargs.pop("model", None)
        super(LDPField, self).__init__(*args, **kwargs)
    
    def to_native(self, instance):
        native = {"@id": "%s%s"%(self.prefix, instance.pk) }
        for field in self.fields:
            native[field] = instance.__getattribute__(field)
        return native
    def from_native(self, instance):
        return self.model.objects.get(pk=instance["@id"].replace(self.prefix, ""))

class IdField(serializers.CharField):
    def to_native(self, value):
        return "%s"%value
    def from_native(self, instance):
        return super(IdField, self).from_native(instance.split("/")[-1])

class ProjectSerializer(serializers.ModelSerializer):
    descendants = LDPField(many=True, required=False, prefix="http://%s/project/ldpcontainer/"%domain, fields=["title"])
    message_set = LDPField(many=True, required=False, prefix="http://%s/message/ldpcontainer/"%domain)
    spec_set = LDPField(many=True, required=False, prefix="http://%s/spec/ldpcontainer/"%domain)
    release_set = LDPField(many=True, required=False, prefix="http://%s/release/ldpcontainer/"%domain, fields=["name", "done"])
    target = LDPField(read_only=False, model=Release, required=False, prefix="http://%s/release/ldpcontainer/"%domain, fields=["name"])
    author = LDPField(required=False, prefix="http://%s/user/ldpcontainer/"%domain)
    state = IdField(required=False)
    
    def __init__(self, *args, **kwargs):
        super(ProjectSerializer, self).__init__(*args, **kwargs)
        self.base_fields['@id'] = IdField(source="id", required=False)
        self.base_fields['ldp:contains'] = LDPField(many=True, required=False, source="tasks", prefix="http://%s/project/ldpcontainer/"%domain, fields=["title"])
    
    class Meta:
        model = Project
        fields = ('@id', 'title', 'author', 'state', 'target', 'ldp:contains', 'descendants', 'spec_set', 'message_set', 'release_set')
