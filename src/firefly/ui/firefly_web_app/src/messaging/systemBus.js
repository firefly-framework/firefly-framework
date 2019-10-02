export default class SystemBus {
    constructor(eventBus, commandBus, queryBus) {
        this.eventBus = eventBus;
        this.commandBus = commandBus;
        this.queryBus = queryBus;
    }

    dispatch(event, data) {
        return this.eventBus.dispatch(event, data);
    }

    invoke(command, data) {
        return this.commandBus.invoke(command, data);
    }

    query(query, data) {
        return this.queryBus.query(query, data);
    }
}
