#
# Copyright (C) 2011-2013 by frePPLe bvba
#
# This library is free software; you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero
# General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public
# License along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import os
import sys
from datetime import datetime
import subprocess

from django.core.management.base import BaseCommand, CommandError
from django.db import DEFAULT_DB_ALIAS
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.template import Template, RequestContext

from freppledb.execute.models import Task
from freppledb.common.models import User
from freppledb import VERSION


class Command(BaseCommand):

  # help = "Loads an XML file into the frePPLe database"
  help = "command not implemented yet"

  # requires_system_checks = False
  #
  # def add_arguments(self, parser):
  #   parser.add_argument(
  #     '--user', help='User running the command'
  #     )
  #   parser.add_argument(
  #     '--database', default=DEFAULT_DB_ALIAS,
  #     help='Nominates a specific database to load data from and export results into'
  #     )
  #   parser.add_argument(
  #     '--task', type=int,
  #     help='Task identifier (generated automatically if not provided)'
  #     )
  #   parser.add_argument(
  #     'file', nargs='+',
  #     help='spreadsheet file name'
  #     )
  #
  #
  # def get_version(self):
  #   return VERSION
  #
  #
  # def handle(self, **options):
  #   # Pick up the options
  #   database = options['database']
  #   if database not in settings.DATABASES:
  #     raise CommandError("No database settings known for '%s'" % database )
  #   if options['user']:
  #     try:
  #       user = User.objects.all().using(database).get(username=options['user'])
  #     except:
  #       raise CommandError("User '%s' not found" % options['user'] )
  #   else:
  #     user = None
  #
  #   now = datetime.now()
  #   task = None
  #   try:
  #     # Initialize the task
  #     if options['task']:
  #       try:
  #         task = Task.objects.all().using(database).get(pk=options['task'])
  #       except:
  #         raise CommandError("Task identifier not found")
  #       if task.started or task.finished or task.status != "Waiting" or task.name != 'export spreadsheet':
  #         raise CommandError("Invalid task identifier")
  #       task.status = '0%'
  #       task.started = now
  #     else:
  #       task = Task(name='export spreadsheet', submitted=now, started=now, status='0%', user=user)
  #     task.arguments = ' '.join(options['file'])
  #     task.save(using=database)
  #
  #     # Execute
  #     # TODO: if frePPLe is available as a module, we don't really need to spawn another process.
  #     os.environ['FREPPLE_HOME'] = settings.FREPPLE_HOME.replace('\\', '\\\\')
  #     os.environ['FREPPLE_APP'] = settings.FREPPLE_APP
  #     os.environ['FREPPLE_DATABASE'] = database
  #     os.environ['PATH'] = settings.FREPPLE_HOME + os.pathsep + os.environ['PATH'] + os.pathsep + settings.FREPPLE_APP
  #     os.environ['LD_LIBRARY_PATH'] = settings.FREPPLE_HOME
  #     if 'DJANGO_SETTINGS_MODULE' not in os.environ:
  #       os.environ['DJANGO_SETTINGS_MODULE'] = 'freppledb.settings'
  #     if os.path.exists(os.path.join(os.environ['FREPPLE_HOME'], 'python35.zip')):
  #       # For the py2exe executable
  #       os.environ['PYTHONPATH'] = os.path.join(
  #         os.environ['FREPPLE_HOME'],
  #         'python%d%d.zip' % (sys.version_info[0], sys.version_info[1])
  #         ) + os.pathsep + os.path.normpath(os.environ['FREPPLE_APP'])
  #     else:
  #       # Other executables
  #       os.environ['PYTHONPATH'] = os.path.normpath(os.environ['FREPPLE_APP'])
  #     cmdline = [ '"%s"' % i for i in options['file'] ]
  #     cmdline.insert(0, 'frepple')
  #     cmdline.append( '"%s"' % os.path.join(settings.FREPPLE_APP, 'freppledb', 'execute', 'loadxml.py') )
  #     (out,ret) = subprocess.run(' '.join(cmdline))
  #     if ret:
  #       raise Exception('Exit code of the batch run is %d' % ret)
  #
  #     # Task update
  #     task.status = 'Done'
  #     task.finished = datetime.now()
  #
  #   except Exception as e:
  #     if task:
  #       task.status = 'Failed'
  #       task.message = '%s' % e
  #       task.finished = datetime.now()
  #     raise e
  #
  #   finally:
  #     if task:
  #       task.save(using=database)

  # accordion template
  title = _('Export a spreadsheet')
  index = 1000

  @ staticmethod
  def getHTML(request):

    javascript = '''
      $(".chck_all").click( function() {
        if ($(this).prop("name") === "alldata") {
          $(".chck_entity[data-tables='data']").prop("checked", $(this).prop("checked"));
        } else if ($(this).prop("name") === "alladmin") {
          $(".chck_entity[data-tables='admin']").prop("checked", $(this).prop("checked"));
        }
      });
      $(".chck_entity").click( function() {
        if ($(this).attr("data-tables") === "data") {
          $(".chck_all[name='alldata']").prop("checked",$(".chck_entity[data-tables='data']:not(:checked)").length === 0);
        } else if ($(this).attr("data-tables") === "admin") {
          $(".chck_all[name='alladmin']").prop("checked",$(".chck_entity[data-tables='admin']:not(:checked)").length === 0);
        }
      });
      '''
    context = RequestContext(request, {'javascript': javascript})

    template = Template('''
      {% load i18n %}
      {% getMenu as menu %}
      <form role="form" method="post" action="{{request.prefix}}/execute/launch/exportworkbook/">{% csrf_token %}
        <table>
        <tr>
          <td style="vertical-align:top; padding: 15px">
              <button type="submit" class="btn btn-primary" id="export" value="{% trans "export"|capfirst %}" >{% trans "export"|capfirst %}</button>
          </td>
          <td style="padding: 15px;">
           <p>
            {% trans "Download all input data in a single spreadsheet." %}
           </p>
            {% getMenu as menu %}
            <p>
            <label>
              <input class="chck_all check" type="checkbox" name="alldata" value="1">&nbsp;<strong>{%trans 'data tables'|upper%}</strong>
            </label><br>
            {% for group in menu %}
              {% for item in group.1 %}
                {% if item.1.model and not item.1.excludeFromBulkOperations and not group.0 == _("admin")%}
                  <label for="chbx_{{ item.1.model | model_name }}">
                    <input class="chck_entity check" data-tables="data" type="checkbox" name="entities" value="{{ item.1.model | model_name }}"{% if item.3 %} checked=""{% endif %} id="chbx_{{ item.1.model | model_name }}">
                      {{ group.0 }} - {{ item.0 }}
                  </label><br>
                {% endif %}
              {% endfor %}
            {% endfor %}
            <label>
              <input class="chck_all check" type="checkbox" checked name="alladmin" value="1">&nbsp;<strong>{%trans 'admin tables'|upper%}</strong>
            </label><br>
            {% for group in menu %}
              {% for item in group.1 %}
                {% if item.1.model and not item.1.excludeFromBulkOperations and group.0 == _("admin")%}
                  <label for="chbx_{{ item.1.model | model_name }}">
                    <input class="chck_entity check" data-tables="admin" type="checkbox" name="entities" value="{{ item.1.model | model_name }}"{% if item.3 %} checked=""{% endif %} id="chbx_{{ item.1.model | model_name }}">
                      {{ group.0 }} - {{ item.0 }}
                  </label><br>
                {% endif %}
              {% endfor %}
            {% endfor %}
            </p>
          </td>
        </tr>
        </table>
      </form>
      <script>{{ javascript|safe }}</script>
    ''')

    return template.render(context)
