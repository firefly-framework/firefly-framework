drop table if exists {% block fqtn %}{{ fqtn | sqlsafe }}{% endblock %}
