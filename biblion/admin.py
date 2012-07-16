from django.contrib import admin
from django.utils.functional import curry

from biblion.models import Blog, Post, Image,Section
from biblion.forms import AdminPostForm
from biblion.utils import can_tweet


class ImageInline(admin.TabularInline):
    model = Image
    fields = ["image_path"]


class PostAdmin(admin.ModelAdmin):  
    list_display = ["blog", "title", "published_flag", "section"]
    list_filter = ["blog", "section"]
    form = AdminPostForm
    fields = [
        "blog",
        "section",
        "title",
        "slug",
        "author",
        "teaser",
        "content",
        "publish",
    ]
    if can_tweet():
        fields.append("tweet")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [
        ImageInline,
    ]
    
    def published_flag(self, obj):
        return bool(obj.published)
    published_flag.short_description = "Published"
    published_flag.boolean = True
    
    def formfield_for_dbfield(self, db_field, **kwargs):
        request = kwargs.get("request")
        if db_field.name == "author":
            ff = super(PostAdmin, self).formfield_for_dbfield(db_field, **kwargs)
            ff.initial = request.user.id
            return ff
        return super(PostAdmin, self).formfield_for_dbfield(db_field, **kwargs)
    
    def get_form(self, request, obj=None, **kwargs):
        kwargs.update({
            "formfield_callback": curry(self.formfield_for_dbfield, request=request),
        })
        return super(PostAdmin, self).get_form(request, obj, **kwargs)
    
    def save_form(self, request, form, change):
        # this is done for explicitness that we want form.save to commit
        # form.save doesn't take a commit kwarg for this reason
        return form.save()


class BlogAdmin(admin.ModelAdmin):
    prepopulated_fields = {
        "slug": ["title"],
    }
class SectionAdmin(admin.ModelAdmin):
    prepopulated_fields = {
        "slug": ["name"],
    }
    
admin.site.register(Post, PostAdmin)
admin.site.register(Image)
admin.site.register(Section,SectionAdmin)
admin.site.register(Blog, BlogAdmin)

