.. _domain:

Domain Layer
============

The domain layer contains the business logic that is specific to your initiative's field
of action, thought or influence. This is the "secret sauce" that your particular application
brings to the world.

The domain layer should be ignorant of any infrastructural concerns. This is accomplished
through the use of interfaces and adapters. For example, if your domain code needed the
contents of a file in your system, you could use Python's built-in functions to read it
from disk. But, what happens when you deploy your code to AWS, where your files are stored
in S3? This code will no longer work. The solution is to create a `FileSystem` interface
that is capable of reading file contents and inject it into your domain code. During
local development you can use a FileSystem implementation that reads from your local disk.
When you deploy to a cloud service provider, you can use another implementation that is
capable of reading from your file storage mechanism of choice.

The domain layer can contain any supporting classes you need. In a typical project, these
will fall into one of two categories: the domain model or domain services. The domain
model consists of entities, value objects and aggregates that make up the virtual
representation of the real-world domain that your are modeling. This is the first place
you should look to put business logic. If, for some reason, a routine does not belong in
an aggregate, entity or value object, then you can put this logic in a domain service.
