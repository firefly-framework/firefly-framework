select

{% if count is true %}
    count(1) as c
{% else %}
    {% for column in columns %}
        {% if ' as ' in column %}
            {{ column | sqlsafe }}
        {% else %}
            {{ _q | sqlsafe }}{{ column | sqlsafe }}{{ _q | sqlsafe }}{% if not loop.last %},{% endif %}
        {% endif %}
    {% endfor %}
{% endif %}

from {% block fqtn %}{{ fqtn | sqlsafe }}{% endblock %}

{% if criteria %}
    where
    {% import "sql/macros.sql" as macros %}
    {% block where_clause scoped %}{{ macros.where_clause(criteria, macros.default_attribute_macro, macros.default_value_macro, ids, field_types) }}{% endblock %}
{% endif %}

{% if count is false %}
    {% if sort %}
        order by
        {% for column in sort %}
            {% block sort_column scoped %}{{ _q | sqlsafe }}{{ column[0] | string | sqlsafe }}{{ _q | sqlsafe }}{% endblock %} {{ 'desc' if column[1] else 'asc' | sqlsafe }}{% if not loop.last %},{% endif %}
        {% endfor %}
    {% endif %}

    {% if limit %}
        limit {{ limit | sqlsafe }}
    {% endif %}

    {% if offset %}
        offset {{ offset | sqlsafe }}
    {% endif %}
{% endif %}