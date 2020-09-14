select

{% if count is true %}
    count(1) as c
{% else %}
    {% for column in columns %}
        {{ _q | sqlsafe }}{{ column | sqlsafe }}{{ _q | sqlsafe }}{% if not loop.last %},{% endif %}
    {% endfor %}
{% endif %}

from {% block fqtn %}{{ fqtn | sqlsafe }}{% endblock %}

{% if criteria %}
    where
    {% import "sql/macros.sql" as macros %}
    {% block where_clause scoped %}{{ macros.where_clause(criteria) }}{% endblock %}
{% endif %}

{% if count is false %}
    {% if sort %}
        order by
        {% for column in sort %}
            {{ _q | sqlsafe }}{{ column[0] | string | sqlsafe }}{{ _q | sqlsafe }} {{ 'desc' if column[1] else 'asc' | sqlsafe }}{% if not loop.last %},{% endif %}
        {% endfor %}
    {% endif %}

    {% if limit %}
        limit {{ limit | sqlsafe }}
    {% endif %}

    {% if offset %}
        offset {{ offset | sqlsafe }}
    {% endif %}
{% endif %}