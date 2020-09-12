insert into {% block fqtn %}{{ fqtn | sqlsafe }} {% endblock %} (

{%- block columns -%}
    {%- for column in data.keys() -%}
        {{ _q | sqlsafe }}{{ column | sqlsafe }}{{ _q | sqlsafe }}{% if not loop.last %},{% endif %}
    {%- endfor -%}
{% endblock %}

) values (

{%- block values -%}
    {%-  for value in data.values() -%}
        {{ value }}{% if not loop.last %},{% endif %}
    {%- endfor -%}
)
{%- endblock -%}
{%- block after -%}{%- endblock -%}
