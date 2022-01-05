&laquo; [Back](../index.md)

# Configuration

Firefly has one primary configuration file, called `firefly.yml` An example config file with all options
is listed below:

```yaml
# This is different from the service name. 
# Often this could be your organization's name.
project: foo
provider: aws

contexts:
  firefly: ~
  firefly_aws:
    region: ${AWS_DEFAULT_REGION}
    
    # Used for code deployments, among other things. 
    # This should be the same across all services in your project.
    bucket: my-bucket-name-${FF_ENVIRONMENT}
    
    # Optional. What memory size should the synchronous function 
    # use? Default: 3072
    memory_sync: 10240 
    
    # Optional. Can also be a memory value, eg "3072". 
    # Default: 3072
    memory_async: adaptive 
    
    # Optional. Only needed if memory_async is set to "adaptive"
    memory_settings:
      # Tells firefly to create a Lambda function with a 
      # 256 MB memory limit.
      - 256
      - 3072
      - 10240
        
    # Optional. Use this to deploy a docker image instead of a 
    # zip file with your code.
    image_uri: ${IMAGE_URI}
    errors: # Deprecated
      email:
        recipients: ${ERROR_RECIPIENTS}

  # This section tells Firefly that we are using a 3rd party 
  # plugin and running it as an extension.
  firefly_plugin_name: 
    is_extension: True

  service_name:
    # Optional. This directive allows you to
    extends: firefly_plugin_name
    
    # Optional. Use this section if you need to configure a 
    # repository for your domain entities.
    storage:
      services:
        # Use a relational database to store entities. (sqlite, 
        # mysql, postgresql) If you name this something other 
        # than rdb, use the "type" setting below.
        rdb:
          
          # Connection info
          connection:
            driver: ${DB_DRIVER}
            host: ${DB_HOST}
            
          # Optional. You can name the service whatever you like, 
          # but if it's non-standard, then you should specify 
          # the type of repository here.
          type: rdb
      default: rdb
      
    # Optional. Route messages to specific functions by name.
    memory_settings:
      default: 256
      "service_name.CommandA": 10240
      "service_name.EventB": 3072

    extensions:
      firefly_aws:
        
        # Anything set here will be added to the env vars 
        # in AWS Lambda.
        environment:
          USER_POOL_ID: ${USER_POOL_ID}
          AWS_MAX_ATTEMPTS: 40
          AWS_RETRY_MODE: adaptive
          FOO: ${FOO}

environments: # Currently unused.
  local: ~
  dev: ~
  staging: ~
  prod: ~

```

Variable substitution is accomplished by embedding your environment variable name in `${}`. When you
run Firefly, it will load your `.env` file along with the variables file that matches your environment
name (eg, `.env.prod`). These variables, along with any other environment variables that are set,
will be used in the substitutions in firefly.yml.
