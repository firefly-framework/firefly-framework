import "./styles.scss";
import m from "mithril";
import {state, actions} from "./store"

const Comp = {
    view() {
        return
    }
};

const Logo = {
    view() {
        return m('div#logo.text-6xl font-sans font-bold text-shadow rambla', [
            m('div.logo-image rounded-full', [
                m('div.firefly one'),
                m('div.firefly two'),
                m('div.firefly three'),
            ]),
            m('span.ml-2', {style: "color: #97B900;"}, 'Fire'),
            m('span.text-orange-500', 'fly')
        ]);
    }
};

const App = {
    view({attrs: {states, actions}}) {
        return m('header.container mx-auto rounded-lg p-4 sticky', [
            m(Logo)
        ])
    }
};

m.mount(document.body, {
    view: () => m(App, { states: state(), actions })
});