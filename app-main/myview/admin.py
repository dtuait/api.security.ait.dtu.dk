from django.contrib import admin
from django.contrib import messages
from django.http import HttpRequest
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.admin.helpers import ActionForm
from django.db import transaction
from django.db import models
from myview.models import ADGroupAssociation
from django.contrib.contenttypes.admin import GenericTabularInline
from django.contrib.contenttypes.models import ContentType
from django.template.response import TemplateResponse
from django.urls import path
from django.utils.html import format_html
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django.shortcuts import redirect
from django import forms
import logging
import ast
import importlib.util
import io
from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path

logger = logging.getLogger(__name__)



try:
    from .models import IPLimiter



except ImportError:
    print("IPLimiter model is not available for registration in the admin site.")
    pass




# Attempt to import the ADGroup model
try:
    from django.contrib import admin
    from django.contrib import messages
    from .models import ADGroupAssociation
    def sync_ad_group_members(modeladmin, request, queryset):
        for obj in queryset:
            ADGroupAssociation.sync_ad_group_members(obj)
        modeladmin.message_user(request, "Selected AD group members synced successfully.", messages.SUCCESS)

        sync_ad_group_members.short_description = "Sync selected AD group members"

    @admin.register(ADGroupAssociation)
    class ADGroupAssociationAdmin(admin.ModelAdmin):
        list_display = ('name', 'canonical_name', 'distinguished_name', 'member_count')  # Fields to display in the admin list view
        search_fields = ('name', 'canonical_name')
        filter_horizontal = ('members',)  # Provides a more user-friendly widget for ManyToMany relations
        readonly_fields = ('name', 'canonical_name', 'distinguished_name', 'member_count')  # Fields that should be read-only in the admin
        list_per_page = 40
        actions = [sync_ad_group_members]


        def get_queryset(self, request):
            # Keep AD groups in sync (cached to avoid frequent LDAP hits)
            try:
                ADGroupAssociation.ensure_groups_synced_cached()
            except Exception:
                logger.exception("AD group cached sync in admin failed")
            qs = super().get_queryset(request)
            return qs.prefetch_related('members')

        def has_delete_permission(self, request, obj=None):
            return True
        
        def has_add_permission(self, request, obj=None):
            return False
        
        def get_readonly_fields(self, request, obj=None):
            if obj:  # This is the case when obj is already created i.e. it's an edit
                return self.readonly_fields + ('members',)
            return self.readonly_fields
        
        def save_model(self, request, obj, form, change):
            # Persist the object before attempting to sync members so that the
            # many-to-many relation can be updated safely. Newly created
            # instances trigger their sync inside the model's save method.
            super().save_model(request, obj, form, change)

            if change:
                obj.sync_ad_group_members()
        def member_count(self, obj):
            return obj.members.count()
        member_count.short_description = 'Member Count'

except ImportError:
    print("ADGroup model is not available for registration in the admin site.")
    pass




try:
    from .models import LimiterType
    @admin.register(LimiterType)
    class LimiterTypeAdmin(admin.ModelAdmin):
        list_display = ('content_type',)
        search_fields = ('name',)
        def save_model(self, request, obj, form, change):
            obj.name = obj.content_type.model_class()._meta.verbose_name
            obj.description = obj.content_type.model_class().__doc__
            super().save_model(request, obj, form, change)


except ImportError:
    print("Limiter type model is not available for registration in the admin site.")
    pass








# Attempt to import the Endpoint model
try:
    from .models import Endpoint


    class EndpointAdminForm(forms.ModelForm):
        class Meta:
            model = Endpoint
            fields = '__all__'

        limiter_content_type = forms.ModelChoiceField(
            queryset=ContentType.objects.filter(model__in=['iplimiter']),
            required=False,
            label="Type of Limiter"
        )
        limiter_object_id = forms.IntegerField(
            required=False,
            label="ID of Limiter"
        )

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            if self.instance and self.instance.limiter:
                self.fields['limiter_content_type'].initial = self.instance.limiter_type
                self.fields['limiter_object_id'].initial = self.instance.limiter_id

        def save(self, commit=True):
            model = super().save(commit=False)
            model.limiter_type = self.cleaned_data['limiter_content_type']
            model.limiter_id = self.cleaned_data['limiter_object_id']
            if commit:
                model.save()
            return model

    # Action form shown in the admin action bar for Endpoints
    class EndpointActionForm(ActionForm):
        limiter_type = forms.ModelChoiceField(
            queryset=LimiterType.objects.all(),
            required=True,
            label="Limiter type",
            help_text="Select the limiter type to apply to selected endpoints.",
        )

    @admin.register(Endpoint)
    class EndpointAdmin(admin.ModelAdmin):
        list_display = ('path', 'method')
        filter_horizontal = ('ad_groups',) 
        readonly_fields = ('path', 'method')
        action_form = EndpointActionForm

        
        formfield_overrides = {
            models.ManyToManyField: {'widget': FilteredSelectMultiple("Relationships", is_stacked=False)},
        }

        @admin.action(description="Set limiter type for selected endpoints")
        def bulk_set_limiter_type(self, request, queryset):
            limiter_type_id = request.POST.get('limiter_type')
            if not limiter_type_id:
                self.message_user(request, "Please choose a limiter type from the action form.", level=messages.ERROR)
                return None
            try:
                lt = LimiterType.objects.get(pk=limiter_type_id)
            except LimiterType.DoesNotExist:
                self.message_user(request, "Selected limiter type no longer exists.", level=messages.ERROR)
                return None

            updated = queryset.update(limiter_type=lt)
            self.message_user(request, _("Updated limiter type for %(count)d endpoint(s).") % {"count": updated}, level=messages.SUCCESS)
            return None

        def save_model(self, request, obj, form, change):

            # Sync members for each group in ad_groups
            ad_groups = form.cleaned_data.get('ad_groups', [])
            for group in ad_groups:
                
                # get or create the group
                try:
                    ad_group_assoc, created = ADGroupAssociation.objects.get_or_create(
                        canonical_name=group.canonical_name,
                        distinguished_name=group.distinguished_name,
                    )
                    print(created)
                except Exception as e:
                    print(f"Error creating ADGroupAssociation: {e}")
                # print ad_group_assoc creted true or false
                
                # add the group to the endpoint
                obj.ad_groups.add(ad_group_assoc)

            # Save the object again to save the changes to ad_groups
            obj.save()

        def formfield_for_manytomany(self, db_field, request, **kwargs):
            if db_field.name == "ad_groups":
                return self._custom_field_logic(db_field, request, ADGroupAssociation, **kwargs)
            # elif db_field.name == "ad_organizational_units":
            #     return self._custom_field_logic(db_field, request, ADOrganizationalUnitAssociation, **kwargs)
            return super().formfield_for_manytomany(db_field, request, **kwargs)

        def _custom_field_logic(self, db_field, request, model_class, **kwargs):
            selected_items = request.session.get(f'ajax_change_form_update_form_{db_field.name}', [])
            associated_items = model_class.objects.filter(endpoints__isnull=False).distinct()
            
            for item in selected_items:
                ad_group_assoc, created = ADGroupAssociation.objects.get_or_create(
                    cn=item['cn'][0],
                    canonical_name=item['canonicalName'][0],
                    defaults={'distinguished_name': item['distinguishedName'][0]}
                )

            if selected_items:
                distinguished_names = [item['distinguishedName'][0] for item in selected_items]
                initial_queryset = db_field.related_model.objects.filter(distinguished_name__in=distinguished_names)
            else:
                initial_queryset = db_field.related_model.objects.all()[:100]

            initial_ids = set(initial_queryset.values_list('id', flat=True))
            associated_ids = set(associated_items.values_list('id', flat=True))
            all_ids = initial_ids | associated_ids
            combined_queryset = db_field.related_model.objects.filter(id__in=all_ids).distinct()

            kwargs["queryset"] = combined_queryset
            return super().formfield_for_manytomany(db_field, request, **kwargs)

        def has_delete_permission(self, request, obj=None):
            return False
        
        def has_add_permission(self, request):
            return False

        # Register actions at class creation time
        actions = ['bulk_set_limiter_type']
        



except ImportError:
    print("Endpoint model is not available for registration in the admin site.")
    pass





















































try:
    from .models import ADOrganizationalUnitLimiter
    from django.contrib import admin
    from django.contrib.admin.widgets import FilteredSelectMultiple
    from django.db import models

    @admin.register(ADOrganizationalUnitLimiter)
    class ADOrganizationalUnitLimiterAdmin(admin.ModelAdmin):
        list_display = ('canonical_name', 'distinguished_name','member_count')
        search_fields = ('canonical_name', 'distinguished_name')
        filter_horizontal = ('ad_groups',)  
        list_per_page = 10  # Display 10 objects per page
        readonly_fields = ('canonical_name', 'distinguished_name')  # Make these fields read-only

        def has_delete_permission(self, request, obj=None):
            return True
        
        def has_add_permission(self, request, obj=None):
            return False
        
        def member_count(self, obj):
            return sum(group.members.count() for group in obj.ad_groups.all())  # Correctly counts the members in all ad_groups
        member_count.short_description = 'Member Count'
except ImportError:
    print("ADOU model is not available for registration in the admin site.")
    pass


UTILITY_SCRIPTS_DIRECTORY = Path(__file__).resolve().parents[1] / "utils"
MAX_OUTPUT_CHARACTERS = 2000
MAX_OUTPUT_LINES = 20


def _format_script_display_name(stem: str) -> str:
    words = stem.replace("_", " ").replace("-", " ")
    words = " ".join(filter(None, words.split()))
    return words.title() if words else stem


def _load_script_docstring(path: Path) -> str:
    try:
        module = ast.parse(path.read_text(encoding="utf-8"))
    except (OSError, SyntaxError) as exc:
        logger.warning("Unable to parse %s for docstring: %s", path.name, exc)
        return ""
    doc = ast.get_docstring(module)
    return doc.strip() if doc else ""


def _list_utility_scripts():
    scripts = []
    if not UTILITY_SCRIPTS_DIRECTORY.exists():
        logger.warning(
            "Utility scripts directory %s does not exist.", UTILITY_SCRIPTS_DIRECTORY
        )
        return scripts

    for path in sorted(UTILITY_SCRIPTS_DIRECTORY.glob("*.py")):
        if path.name == "__init__.py":
            continue
        slug = slugify(path.stem)
        if not slug:
            slug = path.stem
        scripts.append(
            {
                "slug": slug,
                "display_name": _format_script_display_name(path.stem),
                "filename": path.name,
                "path": path,
                "doc": _load_script_docstring(path),
            }
        )

    return scripts


def _get_utility_script(slug: str):
    for script in _list_utility_scripts():
        if script["slug"] == slug:
            return script
    return None


def _load_utility_script_module(script):
    module_name = f"admin_utility_{script['slug'].replace('-', '_')}"
    spec = importlib.util.spec_from_file_location(module_name, script["path"])
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load {script['filename']}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore[attr-defined]
    return module


def _call_utility_script(run_callable):
    buffer = io.StringIO()
    error_message = None
    try:
        with redirect_stdout(buffer), redirect_stderr(buffer):
            run_callable()
    except Exception as exc:  # noqa: BLE001
        error_message = f"{exc.__class__.__name__}: {exc}"
        logger.exception("Utility script raised an error.")
    output = buffer.getvalue().strip()
    return output, error_message


def _trim_script_output(text: str, max_characters: int = MAX_OUTPUT_CHARACTERS, max_lines: int = MAX_OUTPUT_LINES) -> str:
    if not text:
        return ""

    lines = text.splitlines()
    truncated = False

    if len(lines) > max_lines:
        lines = lines[:max_lines]
        truncated = True

    text = "\n".join(lines)

    if len(text) > max_characters:
        text = text[:max_characters].rstrip()
        truncated = True

    if truncated:
        text += "\n…"

    return text


def _format_output_html(text: str):
    return format_html("<pre style=\"white-space: pre-wrap;\">{}</pre>", text)


def utility_scripts_view(request: HttpRequest):
    scripts = _list_utility_scripts()
    context = {
        **admin.site.each_context(request),
        "title": _("Utility scripts"),
        "scripts": scripts,
    }
    return TemplateResponse(request, "admin/utility_scripts.html", context)


def run_utility_script(request: HttpRequest, slug: str):
    if request.method != "POST":
        return redirect("admin:utility-scripts")

    script = _get_utility_script(slug)
    if script is None:
        messages.error(request, _("The requested utility script could not be found."))
        return redirect("admin:utility-scripts")

    try:
        module = _load_utility_script_module(script)
    except ImportError as exc:
        logger.exception("Unable to load utility script %s", script["filename"])
        messages.error(
            request,
            format_html(
                _("Failed to load <strong>{}</strong>: {}"),
                script["display_name"],
                exc,
            ),
        )
        return redirect("admin:utility-scripts")

    run_callable = getattr(module, "run", None)
    if not callable(run_callable):
        messages.error(
            request,
            format_html(
                _("The script <strong>{}</strong> does not define a callable named <code>run()</code>."),
                script["display_name"],
            ),
        )
        return redirect("admin:utility-scripts")

    output, error_message = _call_utility_script(run_callable)
    trimmed_output = _trim_script_output(output)

    if error_message:
        logger.error(
            "Utility script %s executed by %s failed: %s",
            script["filename"],
            request.user,
            error_message,
        )
        message = format_html(
            _("Execution of <strong>{}</strong> failed: {}"),
            script["display_name"],
            error_message,
        )
        if trimmed_output:
            message = format_html("{}<br>{}", message, _format_output_html(trimmed_output))
        messages.error(request, message)
    else:
        logger.info(
            "Utility script %s executed by %s completed successfully.",
            script["filename"],
            request.user,
        )
        message = format_html(
            _("Execution of <strong>{}</strong> completed successfully."),
            script["display_name"],
        )
        if trimmed_output:
            message = format_html("{}<br>{}", message, _format_output_html(trimmed_output))
        messages.success(request, message)

    return redirect("admin:utility-scripts")


def _register_utility_admin_urls():
    original_get_urls = admin.site.get_urls

    def get_urls():
        custom_urls = [
            path("utility-scripts/", admin.site.admin_view(utility_scripts_view), name="utility-scripts"),
            path(
                "utility-scripts/<slug:slug>/run/",
                admin.site.admin_view(run_utility_script),
                name="run-utility-script",
            ),
        ]
        return custom_urls + original_get_urls()

    admin.site.get_urls = get_urls


_register_utility_admin_urls()
