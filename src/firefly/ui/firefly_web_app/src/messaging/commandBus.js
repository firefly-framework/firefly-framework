import MessageBus from "./messageBus";
import {Command} from "./types";

export default class CommandBus extends MessageBus {
    invoke(command, data) {
        if (command instanceof Command) {
            super.dispatch(command);
        } else if (data) {
            super.dispatch(this.messageFactory.command(command, data));
        }
        throw new Error('Invalid arguments to dispatch');
    }
}