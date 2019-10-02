import MiddlewareStack from "./middlewareStack";

export default class MessageBus {
    constructor(middleware, messageFactory) {
        this.middleware = middleware;
        this.stack = new MiddlewareStack(middleware);
        this.messageFactory = messageFactory;
    }

    add(middleware) {
        this.stack.add(middleware);
    }

    insert(index, middleware) {
        this.stack.insert(index, middleware);
    }

    dispatch(message) {
        return this.stack.handle(message);
    }
}