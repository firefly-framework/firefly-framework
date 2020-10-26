alter table {% block fqtn %}{{ fqtn | sqlsafe }}{% endblock %} drop column {{ _q | sqlsafe }}{{ column.name | sqlsafe }}{{ _q | sqlsafe }}
