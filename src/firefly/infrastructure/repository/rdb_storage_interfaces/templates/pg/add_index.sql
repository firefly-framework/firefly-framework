{% extends 'sql/add_index.sql' %}
{% block index_fields %}
    {% for column in index.columns %}
        ({{ _q | sqlsafe }}document{{ _q | sqlsafe }}->'{{ column | sqlsafe }}')
        {% if not loop.last %},{% endif %}
    {% endfor %}
{% endblock %}