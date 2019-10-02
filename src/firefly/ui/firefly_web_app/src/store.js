import stream from "mithril/stream";

const app = {
    Initial: () => ({
        counter: 1,
    }),
    Actions: update => ({
        inc(amount) {
            update(function(state) {
                state.counter += amount;
                return state;
            });
        },
    }),
};

export const update = stream();
export const state = stream.scan((state, patch) => patch(state), app.Initial(), update);
export const actions = app.Actions(update);