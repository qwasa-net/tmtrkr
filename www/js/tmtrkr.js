const API_URL = "/api";
const tmtrkr_app = Vue.createApp({
    data() {
        return {
            data: null,
            active_record: null,
            filter: {
                start_a: null,
                start_b: null,
                q: null
            },
            user_active: null,
            users: {
                listing: null,
                selected: null
            },
            status_message: null,
            timezone: null,
            timezone_local: null,
            locale: [],
            show: {
                weeks: true,
            }
        }
    },

    mounted() {
        this.init();
    },

    computed: {

        timezone_name() {
            return this.timezone || "UTC";
        },

        locale_name() {
            if (!this.locale || !this.locale.length) {
                return "default";
            }
            return this.locale;
        },

        records_by_day() {
            if (!this.data || !this.data.records || !this.data.records.length) {
                return {};
            }
            let records = this.data.records;
            let by_day = {};
            for (let i = 0; i < records.length; i++) {
                let r = records[i];
                let day = this.ts_date_fmt(r.start);
                if (day in by_day) {
                    by_day[day].push(r);
                } else {
                    by_day[day] = [r];
                }
            }
            return by_day;
        }
    },

    methods: {

        init() {
            this.timezone_local = Intl.DateTimeFormat().resolvedOptions().timeZone;
            this.timezone_offset = (new Date()).getTimezoneOffset();
            this.timezone = this.timezone_local;
            this.update();
        },

        update() {
            this.status_message = null;
            this.get_records();
            if (!this.user_active) {
                this.get_users();
            }
        },

        get_records() {
            let qs = {};

            if (this.filter.start_a) {
                let start_a_ts = (new Date(this.filter.start_a).getTime() / 1000);
                start_a_ts += 0 * 60 * 60; // (from 00:00:00)
                if (this.timezone && this.timezone_offset) {
                    start_a_ts += this.timezone_offset * 60;
                }
                qs.start_min = start_a_ts;
            }
            if (this.filter.start_b) {
                let start_b_ts = (new Date(this.filter.start_b).getTime() / 1000);
                start_b_ts += 24 * 60 * 60 - 1; // (till 23:59:59)
                if (this.timezone && this.timezone_offset) {
                    start_b_ts += this.timezone_offset * 60;
                }
                qs.start_max = start_b_ts;
            }

            let records_url = API_URL + '/records/';
            let url = records_url + "?" + String(new URLSearchParams(qs));
            this.data = null;

            fetch(url, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    ...this.auth_headers()
                },
            })
                .then(rsp => {
                    rsp.json().then(data => {
                        if (rsp.ok) {
                            this.data = data;
                            if (data.user && !this.user_active) {
                                this.user_active = { name: data.user.name };
                            }
                        } else {
                            this.status_message = `Get records failed: ${rsp.status} ${rsp.statusText}`;
                        }
                    })
                })
                .catch((error) => {
                    console.error(error);
                    this.status_message = error;
                });
        },

        edit_record(record) {
            let ac = Object.assign({}, record);
            ac.start_input = ac.start && this.ts_yymdhms(this.ts_date(ac.start));
            ac.end_input = ac.end && this.ts_yymdhms(this.ts_date(ac.end));
            this.active_record = ac;
        },

        create_record() {
            let now = new Date();
            now.setSeconds(0);
            let now_ts = now.valueOf() / 1000;
            let record = {
                name: '…',
                tags: '',
                start: Math.floor(now_ts / (60 * 10)) * 60 * 10,
                end: null
            };
            this.edit_record(record);
        },

        close_active_record() {
            this.active_record = null;
        },

        delete_record() {
            let ac = this.active_record;
            if (!ac) {
                return;
            }
            this.active_record.delete_id = this.active_record.id;
        },

        delete_confirmed_record() {
            let ac = this.active_record;
            if (!ac) {
                return;
            }
            let url = API_URL + `/records/${ac.delete_id}`;
            fetch(url, {
                method: "DELETE",
                headers: {
                    'Content-Type': 'application/json',
                    ...this.auth_headers()
                },
            })
                .then(rsp => {
                    rsp.json().then(data => {
                        if (rsp.ok && data) {
                            this.active_record = null;
                            this.get_records();
                        } else {
                            this.active_record.errors = `Delete failed: ${rsp.status} ${rsp.statusText}: ${JSON.stringify(data || null)}`;
                        }
                    })
                })
                .catch((error) => {
                    console.error(error);
                    this.status_message = error;
                });
        },

        validate_active_record() {
            let ac = this.active_record;
            if (!ac) {
                return;
            }
            ac.start = ac.start_input ? (new Date(ac.start_input).getTime() / 1000) : null;
            ac.end = ac.end_input ? (new Date(ac.end_input).getTime() / 1000) : null;
            if (ac.start && ac.end) {
                ac.duration = ac.end - ac.start;
            } else {
                ac.duration = null;
            }
        },

        save_record() {
            let ac = this.active_record;
            if (!ac) {
                return;
            }
            let data = {
                start: (new Date(ac.start_input).getTime() / 1000),
                end: ac.end_input ? (new Date(ac.end_input).getTime() / 1000) : null,
                name: ac.name,
                tags: ac.tags,
            };
            let url = API_URL + '/records/';
            let method = "POST";
            if (ac.id) {
                url += String(ac.id);
                method = "PATCH";
            }
            fetch(url, {
                method: method,
                cache: 'no-cache',
                headers: {
                    'Content-Type': 'application/json',
                    ...this.auth_headers()
                },
                body: JSON.stringify(data)
            })
                .then(rsp => {
                    rsp.json().then(data => {
                        if (rsp.ok && data) {
                            this.active_record = null;
                            this.get_records();
                        } else {
                            this.active_record.errors = `Save failed: ${rsp.status} ${rsp.statusText}: ${JSON.stringify(data || null)}`;
                        }
                    })
                })
                .catch((error) => {
                    console.error(error);
                    this.active_record.errors = error;
                });
        },

        save_as_new_record() {
            let ac = this.active_record;
            if (!ac) {
                return;
            }
            ac.id = null;
            this.save_record();
        },

        active_record_set_tm(tm, field, field2) {
            let ac = this.active_record;
            if (!ac) {
                return;
            }
            field = field || 'start';
            field2 = field2 || 'start';
            let today = (new Date());
            let start = (new Date(ac[field] * 1000));
            if (tm == "now") {
                today.setSeconds(0);
                ac[field] = today.valueOf() / 1000;
            } else if (tm == "today") {
                start.setDate(today.getDate());
                start.setMonth(today.getMonth());
                start.setFullYear(today.getFullYear());
                start.setSeconds(0);
                ac[field] = start.valueOf() / 1000;
            } else if (tm == "noon") {
                start.setHours(12);
                start.setMinutes(0);
                start.setSeconds(0);
                ac[field] = start.valueOf() / 1000;
            } else if (tm == "same") {
                ac[field] = ac[field2];
            } else if (tm == "clear") {
                ac[field] = null;
            } else if (typeof tm == 'number') {
                ac[field] += Number(tm);
            }
            ac[field + "_input"] = ac[field] && this.ts_yymdhms(this.ts_date(ac[field]));
            this.validate_active_record();
        },

        active_record_scroll_tm(field, event) {
            let delta_y = Number(event.deltaY) || 0;
            let shift_key = Boolean(event.shiftKey);
            let tm = shift_key ? (24 * 60 * 60) : (10 * 60);
            if (delta_y) {
                this.active_record_set_tm(Math.sign(delta_y) * tm, field);
            }
        },

        get_users() {
            let url = API_URL + '/users/';
            fetch(url, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    ...this.auth_headers()
                },
            })
                .then(rsp => rsp.json())
                .then(data => {
                    this.users.listing = data.users;
                    console.log(this.users);
                })
                .catch((error) => {
                    console.error(error);
                });
        },

        user_logout() {
            let url = API_URL + '/users/logout';
            fetch(url, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    ...this.auth_headers()
                },
            })
                .then((rsp) => {
                    this.user_active = null;
                    this.users.selected = null;
                    this.update();
                    this.status_message = "Logged-out.";
                })
                .catch((error) => {
                    console.error(error);
                });
        },

        user_signup() {
            let username = prompt("Username");
            if (username) {
                this.user_active = {
                    "name": username,
                    "token": null,
                };
                this.user_login();
            }
        },

        user_switch() {
            if (this.users && this.users.selected) {
                this.user_active = {
                    "name": this.users.selected,
                    "token": null,
                };
                this.user_login();
            } else {
                this.user_active = null;
            }
        },

        user_login() {
            let url = API_URL + '/users/token';

            fetch(url, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Forwarded-User': this.user_active.name
                },
            })
                .then(rsp => {
                    if (rsp.ok) {
                        rsp.json().then(data => {
                            this.user_active.token = data.token;
                            this.update();
                            this.status_message = `Logged-in as ${this.user_active.name}`;
                        });
                    } else {
                        this.status_message = `Login failed: ${rsp.status} ${rsp.statusText}`
                    }
                })
                .catch((error) => {
                    console.error(error);
                    this.status_message = error;
                    this.user_logout();
                });
        },

        auth_headers() {
            let headers = {};
            if (this.user_active && this.user_active.token) {
                headers["Authorization"] = `Bearer ${this.user_active.token}`;
            }
            return headers;
        },

        print() {
            let title_parts = ["TmTrkr"];
            if (this.user_active) {
                title_parts.push(`${this.user_active.name || "-"}`);
            }
            if (this.filter && this.filter.start_a && this.filter.start_b) {
                let a = this.ts_date(this.filter.start_a);
                let b = this.ts_date(this.filter.start_b);
                title_parts.push(`${this.ts_yymd(a)}-${this.ts_yymd(b)}`);
            }
            document.title = title_parts.join("_");
            window.print();
        },

        toggle_timezone() {
            if (this.timezone) {
                this.timezone = null;
            } else {
                this.timezone = this.timezone_local;
            }
            this.update();
        },

        toggle_locale() {
            if (!this.locale || !this.locale.length) {
                this.locale = ["en-US",];
            } else {
                this.locale = [];
            }
        },

        toggle_weeks() {
            this.show.weeks = !this.show.weeks;
        },

        duration_hours_fmt(secs) {
            let h = secs / (60 * 60);
            return h.toFixed(2);
        },

        duration_fmt(secs, skip_days) {
            if (!secs) {
                return '-';
            }
            let negative = (secs < 0) ? true : false;
            secs = Math.abs(secs);
            let d = Math.floor(secs / (60 * 60 * 24));
            if (skip_days) {
                d = 0;
            }
            let h = Math.floor((secs - d * (60 * 60 * 24)) / (60 * 60));
            let m = Math.floor((secs - d * (60 * 60 * 24) - h * (60 * 60)) / (60));
            let s = Math.floor(secs % 60);
            if (d) {
                str = `${d}d ${pad0(h)}h:${pad0(m)}m`;
            } else {
                str = `${pad0(h)}h:${pad0(m)}m`;
            }
            if (s) {
                str += `:${pad0(s)}`;
            }
            if (negative) {
                str = `-${str}`;
            }
            return str;
        },

        ts_date(ts) {
            if (typeof ts == 'number') {
                return new Date(ts * 1000);
            } else if (typeof ts == 'string') {
                return new Date(ts);
            } else {
                return new Date();
            }
        },

        ts_date_fmt(ts) {
            let options = {
                dateStyle: 'long',
                timeZone: this.timezone || "UTC",
            };
            let dt = this.ts_date(ts);
            return dt.toLocaleString(this.locale, options);
        },

        ts_time_fmt(ts) {
            let options = {
                hour: 'numeric',
                minute: 'numeric',
                hour12: false,
                // timeZoneName: 'short',
                timeZone: this.timezone || "UTC",
            };
            let dt = this.ts_date(ts);
            return dt.toLocaleString(this.locale, options);
        },

        ts_week_fmt(ts) {
            let dt = this.ts_date(ts);
            let j4 = new Date(dt.getFullYear(), 0, 4);
            let date = new Date(dt.getFullYear(), dt.getMonth(), dt.getDate());
            let week_number = 1 + Math.round(((date.getTime() - j4.getTime()) / 86400000 - 3 + (j4.getDay() + 6) % 7) / 7);
            return week_number;
        },

        ts_fmt(ts, timezone) {
            let options = {
                // dateStyle: 'short',
                // timeStyle: 'short',
                year: "numeric",
                month: 'short',
                day: 'numeric',
                weekday: 'short',
                hour: 'numeric',
                minute: 'numeric',
                timeZoneName: 'short',
                timeZone: timezone || this.timezone || "UTC",
                hour12: false,
            };
            let dt = this.ts_date(ts);
            return dt.toLocaleString(this.locale, options);
        },

        ts_yymdhms(dt) {
            let ymdhms = `${pad0(dt.getFullYear(), 4)}-${pad0((1 + dt.getMonth()))}-${pad0(dt.getDate())}T${pad0(dt.getHours())}:${pad0(dt.getMinutes())}:${pad0(dt.getSeconds())}`;
            return ymdhms;
        },

        ts_yymd(dt) {
            let ymd = `${pad0(dt.getFullYear(), 4)}-${pad0((1 + dt.getMonth()))}-${pad0(dt.getDate())}`;
            return ymd;
        }
    }
});

function pad0(s, l, p, fb) {
    try {
        return s.toString().padStart(l || 2, p || '0')
    } catch {
        return fb;
    }
}

tmtrkr_app.mount('#tmtrkr_app');
