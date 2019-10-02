import MessageBus from "./messageBus";
import {Event} from "./types";

export default class EventBus extends MessageBus {
    dispatch(event, data) {
        if (event instanceof Event) {
            super.dispatch(event);
        } else if (data) {
            super.dispatch(this.messageFactory.event(event, data));
        }
        throw new Error('Invalid arguments to dispatch');
    }
}