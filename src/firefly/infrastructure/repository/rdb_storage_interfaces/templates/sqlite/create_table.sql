{% extends 'sql/create_table.sql' %}
    {% block fqtn %}{{ fqtn.replace('.', '_') | sqlsafe }}{% endblock %}