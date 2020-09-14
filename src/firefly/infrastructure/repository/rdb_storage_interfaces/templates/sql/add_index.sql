create {% if index.unique %}unique{% endif %} index {% block index_name scoped %}{{ _q | sqlsafe }}{{ index.name | sqlsafe }}{{ _q | sqlsafe }}{% endblock %}

on {% block fqtn %}{{ fqtn | sqlsafe }}{% endblock %} (
    {% for column in index.columns %}
        {{ _q | sqlsafe }}{{ column | sqlsafe }}{{ _q | sqlsafe }}{% if not loop.last %},{% endif %}
    {% endfor %}
)
