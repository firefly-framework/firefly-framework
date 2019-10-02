import {Event, Command, Query} from "./types";

class MessageFactory {
    event(name, data) {
        return this._build(name, data, Event.prototype);
    }

    command(name, data) {
        return this._build(name, data, Command.prototype);
    }

    query(name, data) {
        return this._build(name, data, Query.prototype);
    }

    _build(name, data, proto) {
        const ret = function() {
            this._name = name;
            Object.assign(this, data);
        };
        ret.prototype = proto;
        return new ret();
    }
}

const messageFactory = new MessageFactory();

export default messageFactory;