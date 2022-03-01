{% extends 'sql/add_index.sql' %}
{% block index_fields %}
    {% for column in index.columns %}
        {% if field_types[column] == 'datetime' %}
            ff_datetime({{ _q | sqlsafe }}document{{ _q | sqlsafe }}->>'{{ column | sqlsafe }}')
        {% elif field_types[column] == 'date' %}
            ff_date({{ _q | sqlsafe }}document{{ _q | sqlsafe }}->>'{{ column | sqlsafe }}')
        {% else %}
            ({{ _q | sqlsafe }}document{{ _q | sqlsafe }}->>'{{ column | sqlsafe }}')
        {% endif %}
        {% if not loop.last %},{% endif %}
    {% endfor %}
{% endblock %}