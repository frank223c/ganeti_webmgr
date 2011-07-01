# Copyright (C) 2010 Oregon State University et al.
# Copyright (C) 2010 Greek Research and Technology Network
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301,
# USA.

from django.conf.urls.defaults import patterns, url
from haystack.views import SearchView
from django.contrib.auth.decorators import login_required
import os
from forms.autocomplete_search_form import autocomplete_search_form


cluster_slug = '(?P<cluster_slug>[-_A-Za-z0-9]+)'
cluster = 'cluster/%s' % cluster_slug

primary_node = 'primary_node/(?P<primary_node>.+)'
secondary_node = 'secondary_node/(?P<secondary_node>.+)'

instance = '(?P<instance>[^/]+)'
host = '(?P<host>[^/]+)'

# General
urlpatterns = patterns('ganeti_web.views.general',
    #   Index page - it's status page
    url(r'^$', 'overview', name="index"),
    #   Status page
    url(r'^overview/?$', 'overview', name="overview"),
    url(r'^used_resources/?$', 'used_resources', name="used_resources"),
    
    # clear errors
    url(r'^error/clear/(?P<pk>\d+)/?$', 'clear_ganeti_error', name="error-clear"),

    #About page
    url(r'^about/?$', 'about', name="about"),
)


# Users - overridden from users app to use custom templates
urlpatterns += patterns('muddle_users.views.user',
    url(r'^accounts/profile/?', 'user_profile', name='profile',
        kwargs={'template':'ganeti/users/profile.html'}),
)

# Users
urlpatterns += patterns('ganeti_web.views.users',
    url(r'^user/(?P<user_id>\d+)/key/?$', 'key_get', name="user-key-add"),

    # ssh keys
    url(r'^keys/get/$',                     'key_get', name="key-get"),
    url(r'^keys/get/(?P<key_id>\d+)/?$',    'key_get', name="key-get"),
    url(r'^keys/save/$',                    'key_save', name="key-save"),
    url(r'^keys/save/(?P<key_id>\d+)/?$',   'key_save', name="key-save"),
    url(r'^keys/delete/(?P<key_id>\d+)/?$', 'key_delete', name="key-delete"),
)

# All SSH Keys
urlpatterns += patterns('ganeti_web.views.general',
    url(r'^keys/(?P<api_key>\w+)/$', 'ssh_keys', name="key-list"),
)

#Groups
urlpatterns += patterns('muddle_users.views.group',
    url(r'^group/(?P<id>\d+)/?$', 'detail',
            {'template':'ganeti/group/detail.html'},
            name="group-detail"),
)

# Clusters
urlpatterns += patterns('ganeti_web.views.cluster',
    #   List
    url(r'^clusters/?$', 'list_', name="cluster-list"),
    #   Add
    url(r'^cluster/add/?$', 'edit', name="cluster-create"),
    #   Detail
    url(r'^%s/?$' % cluster, 'detail', name="cluster-detail"),
    #   Edit
    url(r'^%s/edit/?$' % cluster, 'edit', name="cluster-edit"),
    #   Redistribute config
    url(r'^%s/redistribute-config/?$' % cluster, 'redistribute_config', name="cluster-redistribute-config"),
    #   User
    url(r'^%s/users/?$' % cluster, 'users', name="cluster-users"),
    url(r'^%s/virtual_machines/?$' % cluster, 'virtual_machines', name="cluster-vms"),
    url(r'^%s/nodes/?$' % cluster, 'nodes', name="cluster-nodes"),
    url(r'^%s/quota/(?P<user_id>\d+)?/?$'% cluster, 'quota', name="cluster-quota"),
    url(r'^%s/permissions/?$' % cluster, 'permissions', name="cluster-permissions"),
    url(r'^%s/permissions/user/(?P<user_id>\d+)/?$' % cluster, 'permissions', name="cluster-permissions-user"),
    url(r'^%s/permissions/group/(?P<group_id>\d+)/?$' % cluster, 'permissions', name="cluster-permissions-group"),

    #ssh_keys
    url(r'^%s/keys/(?P<api_key>\w+)/?$' % cluster, "ssh_keys", name="cluster-keys"),

    # object log
    url(r'^%s/object_log/?$' % cluster, 'object_log', name="cluster-object_log"),
)


# Nodes
node_prefix = 'cluster/%s/node/%s' %  (cluster_slug, host)
urlpatterns += patterns('ganeti_web.views.node',
    # Detail
    url(r'^%s/?$' % node_prefix, 'detail', name="node-detail"),
    url(r'^node/(?P<id>\d+)/?$', 'detail_by_id', name="node-detail-id"),
    
    # Primary and secondary Virtual machines
    url(r'^%s/primary/?$' % node_prefix, 'primary', name="node-primary-vms"),
    url(r'^%s/secondary/?$' % node_prefix, 'secondary', name="node-secondary-vms"),

    #object log
    url(r'^%s/object_log/?$' % node_prefix, 'object_log', name="node-object_log"),

    # Node actions
    url(r'^%s/role/?$' % node_prefix, 'role', name="node-role"),
    url(r'^%s/migrate/?$' % node_prefix, 'migrate', name="node-migrate"),
    url(r'^%s/evacuate/?$' % node_prefix, 'evacuate', name="node-evacuate"),
)

template_id = '(?P<template_id>\d+)'
# VirtualMachineTemplates
urlpatterns += patterns('ganeti_web.views.vm_template',
    # List
    url(r'^templates/$', 'templates', name='template-list'),
    # Detail
    url(r'^template/%s/?$' % template_id, 'detail', name='template-detail'),
    # Delete
    url(r'^template/%s/delete/?$' % template_id, 'delete', name='template-delete'),
    # Create
    url(r'^template/create/$', 'create', name='template-create'),
    url(r'^template/create/%s/$' % instance, 'create_from_instance', name='template-create-from-instance'),
    # Edit
    url(r'^template/edit/%s/?$' % template_id, 'create', name='template-edit'),
    # Copy
    url(r'^template/copy/%s/?$' % template_id, 'copy', name='template-copy'),
)

# VirtualMachines
vm_prefix = '%s/%s' %  (cluster, instance)
urlpatterns += patterns('ganeti_web.views.virtual_machine',
    #  List
    url(r'^vms/$', 'list_', name="virtualmachine-list"),
    #  Create
    url(r'^vm/add/?$', 'create', name="instance-create"),
    url(r'^vm/add/choices/$', 'cluster_choices', name="instance-create-cluster-choices"),
    url(r'^vm/add/options/$', 'cluster_options', name="instance-create-cluster-options"),
    url(r'^vm/add/defaults/$', 'cluster_defaults', name="instance-create-cluster-defaults"),
    url(r'^vm/add/template/%s/$' % template_id, 'create_from_template', name="instance-create-from-template"),
    url(r'^vm/add/%s/?$' % cluster_slug, 'create', name="instance-create"),
    url(r'^%s/recover/?$' % vm_prefix, 'recover_failed_deploy', name="instance-create-recover"),

    #  VM Table
    url(r'^%s/vm/table/?$' % cluster, 'vm_table', name="cluster-virtualmachine-table"),
    url(r'^vm/table/$', 'vm_table', name="virtualmachine-table"),
    url(r'^vm/table/%s/?$' % primary_node, 'vm_table', name="vm-table-primary"),
    url(r'^vm/table/%s/?$' % secondary_node, 'vm_table', name="vm-table-secondary"),

    #  Detail
    url(r'^%s/?$' % vm_prefix, 'detail', name="instance-detail"),
    url(r'^vm/(?P<id>\d+)/?$', 'detail_by_id', name="instance-detail-id"),
    url(r'^%s/users/?$' % vm_prefix, 'users', name="vm-users"),
    url(r'^%s/permissions/?$' % vm_prefix, 'permissions', name="vm-permissions"),
    url(r'^%s/permissions/user/(?P<user_id>\d+)/?$' % vm_prefix, 'permissions', name="vm-permissions-user"),
    url(r'^%s/permissions/group/(?P<group_id>\d+)/?$' % vm_prefix, 'permissions', name="vm-permissions-user"),
    
    #  Start, Stop, Reboot, VNC
    url(r'^%s/vnc/?$' % vm_prefix, 'novnc', name="instance-vnc"),
    url(r'^%s/vnc_proxy/?$' % vm_prefix, 'vnc_proxy', name="instance-vnc-proxy"),
    url(r'^%s/shutdown/?$' % vm_prefix, 'shutdown', name="instance-shutdown"),
    url(r'^%s/startup/?$' % vm_prefix, 'startup', name="instance-startup"),
    url(r'^%s/reboot/?$' % vm_prefix, 'reboot', name="instance-reboot"),
    url(r'^%s/migrate/?$' % vm_prefix, 'migrate', name="instance-migrate"),

    # Delete
    url(r"^%s/delete/?$" % vm_prefix, "delete", name="instance-delete"),

    # Reinstall
    url(r"^%s/reinstall/?$" % vm_prefix, "reinstall", name="instance-reinstall"),
    
    # Edit / Modify
    url(r"^%s/edit/?$" % vm_prefix, "modify", name="instance-modify"),
    url(r'^%s/edit/confirm/?$' % vm_prefix, "modify_confirm", name="instance-modify-confirm"),
    url(r"^%s/rename/?$" % vm_prefix, "rename", name="instance-rename"),
    url(r"^%s/reparent/?$" % vm_prefix, "reparent", name="instance-reparent"),
    
    # SSH Keys
    url(r'^%s/keys/(?P<api_key>\w+)/?$' % vm_prefix, "ssh_keys", name="instance-keys"),
    
    # object log
    url(r'^%s/object_log/?$' % vm_prefix, 'object_log', name="vm-object_log"),
)


# Virtual Machine Importing
urlpatterns += patterns('ganeti_web.views.importing',
    url(r'^import/orphans/', 'orphans', name='import-orphans'),
    url(r'^import/missing/', 'missing_ganeti', name='import-missing'),
    url(r'^import/missing_db/', 'missing_db', name='import-missing_db'),
)

# Node Importing
urlpatterns += patterns('ganeti_web.views.importing_nodes',
    url(r'^import/node/missing/', 'missing_ganeti', name='import-nodes-missing'),
    url(r'^import/node/missing_db/', 'missing_db', name='import-nodes-missing_db'),
)

# Jobs
job = '%s/job/(?P<job_id>\d+)' % cluster
urlpatterns += patterns('ganeti_web.views.jobs',
    url(r'^%s/status/?' % job, 'status', name='job-status'),
    url(r'^%s/clear/?' % job, 'clear', name='job-clear'),
    url(r'^%s/?' % job, 'detail', name='job-detail'),
)

# Search
urlpatterns += patterns('ganeti_web.views.search',
    url(r'^search/suggestions.json', 'suggestions', name='search-suggestions'),
    url(r'^search/detail_lookup', 'detail_lookup', name='search-detail-lookup')
)
urlpatterns += patterns('haystack.views',
    url(r'^search/', login_required(SearchView(form_class=autocomplete_search_form)), name='search')
)


#The following is used to serve up local media files like images
root = '%s/media' % os.path.dirname(os.path.realpath(__file__))
urlpatterns += patterns('',
    (r'^ganeti_web_media/(?P<path>.*)', 'django.views.static.serve',
     {'document_root':  root}),
)
