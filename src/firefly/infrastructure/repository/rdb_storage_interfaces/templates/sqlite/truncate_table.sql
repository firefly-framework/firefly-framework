{% extends 'sql/truncate_table.sql' %}
    {% block fqtn %}{{ fqtn.replace('.', '_') | sqlsafe }}{% endblock %}