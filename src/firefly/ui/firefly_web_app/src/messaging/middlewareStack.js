export default class MiddlewareStack {
    constructor(middleware) {
        this.middleware = middleware || [];
    }

    add(middleware) {
        this.middleware.push(middleware);
    }

    insert(index, middleware) {
        this.middleware.splice(index, 0, middleware);
    }

    handle(message) {
        let cb = (message) => message;
        this.middleware.reverse().forEach((mw) => {
            const n = cb;
            cb = (message) => mw(message, n);
        });
        return cb(message);
    }
}
