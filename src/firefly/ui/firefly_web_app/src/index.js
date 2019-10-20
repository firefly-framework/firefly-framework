/*
 * Copyright (c) 2019 JD Williams
 *
 * This file is part of Firefly, a Python SOA framework built by JD Williams. Firefly is free software; you can
 * redistribute it and/or modify it under the terms of the GNU General Public License as published by the
 * Free Software Foundation; either version 3 of the License, or (at your option) any later version.
 *
 * Firefly is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the
 * implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General
 * Public License for more details. You should have received a copy of the GNU Lesser General Public
 * License along with this program.  If not, see <http://www.gnu.org/licenses/>.
 *
 * You should have received a copy of the GNU General Public License along with Firefly. If not, see
 * <http://www.gnu.org/licenses/>.
 */

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