import MessageBus from "./messageBus";
import {Query} from "./types";

export default class QueryBus extends MessageBus {
    query(query, data) {
        if (query instanceof Query) {
            super.dispatch(query);
        } else if (data) {
            super.dispatch(this.messageFactory.query(query, data));
        }
        throw new Error('Invalid arguments to dispatch');
    }
}