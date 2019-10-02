import Entity from "firefly-framework/src/domain/entity/entity";

export default class User extends Entity {
    constructor({name}) {
        super();
        this.name = name;
    }
}