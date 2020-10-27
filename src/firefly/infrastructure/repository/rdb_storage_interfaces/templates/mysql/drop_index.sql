drop index {% block index_name scoped %}{{ _q | sqlsafe }}{{ index.name | sqlsafe }}{{ _q | sqlsafe }}{% endblock %} on {{ fqtn | sqlsafe }}
