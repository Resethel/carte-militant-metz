from django.shortcuts import render
from django.views.generic import DetailView

from core.models import Organization
from map_thematics.models import Thematic


# ======================================================================================================================
# Vue de la page d'accueil
# ======================================================================================================================

def home(request):
    return render(request, 'core/home.html')

# ======================================================================================================================
# Vues des organisations ayant participé à la cartographie
# ======================================================================================================================

class OrganizationDetailView(DetailView):
    model = Organization
    template_name = 'core/resume.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        org_obj : Organization = self.object

        context['title']       = org_obj.name
        context['photo']       = org_obj.logo
        context['categories']  = [org_obj.type]
        context['body']        = org_obj.description
        context['social_links'] = []
        if org_obj.contact:
            context['social_links'].append({'name': 'email', 'url': org_obj.contact})
        if org_obj.website:
            context['social_links'].append({'name': 'website', 'url': org_obj.website})
        if org_obj.facebook:
            context['social_links'].append({'name': 'facebook', 'url': org_obj.facebook})
        if org_obj.twitter:
            context['social_links'].append({'name': 'twitter', 'url': org_obj.twitter})
        if org_obj.instagram:
            context['social_links'].append({'name': 'instagram', 'url': org_obj.instagram})

        return context
# End class OrganizationDetailView

def organizations_list(request):
    organizations = Organization.objects.all()
    return render(request, 'core/organizations_list.html', {'organizations': organizations})
