import Vue from 'vue'
import Router from 'vue-router'
import Menu from '@/components/Menu'
import Translate from '@/components/Translate'

Vue.use(Router)

export default new Router({
    mode: 'history',
    routes: [{
        path: '/',
        redirect: '/menu'
    }, {
        path: '/menu',
        name: 'Menu',
        component: Menu
    }, {
        path: '/translate/:id',
        name: 'Translate',
        component: Translate
    }]
})