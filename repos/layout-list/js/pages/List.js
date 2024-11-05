import { store } from '../main.js';
import { embed, rgbaBind, localize } from '../util.js';
import { score, lightPackColor, darkPackColor } from '../config.js';
import { fetchStaff, averageEnjoyment, fetchHighestEnjoyment, fetchLowestEnjoyment, fetchTotalScore, fetchTierLength, fetchTierMinimum } from '../content.js';
import Spinner from '../components/Spinner.js';
import LevelAuthors from '../components/List/LevelAuthors.js';

const roleIconMap = {
    owner: 'crown',
    admin: 'user-gear',
    helper: 'user-shield',
    dev: 'code',
    trial: 'user-lock',
};


export default {
    components: { Spinner, LevelAuthors },
    template: `
        <main v-if="loading">
            <Spinner></Spinner>
        </main>
        <main v-else class="page-list">
            <div class="list-container">
                <table class="list" v-if="list">
                    <tr v-for="([err, rank, level], i) in list">
                        <td class="rank">
                            <p v-if="rank === null" class="type-label-lg">&mdash;</p>
                            <p v-else class="type-label-lg">#{{ rank }}</p>
                        </td>
                        <td class="level" :class="{ 'active': selected == i, 'error': err !== null }">
                            <button @click="selected = i">
                                <span class="type-label-lg">{{ level?.name || 'Error (' + err + '.json)' }}</span>
                            </button>
                        </td>
                    </tr>
                </table>
            </div>
            <div class="level-container">
                <div class="level" v-if="level && level.id!=0">
                    <h1>{{ level.name }}</h1>
                    <div class="pack-container" v-if="level.packs.length > 1 || level.packs.length !== 0 && level.packs[0].levels">
                        <div class="pack" v-for="pack in level.packs" :style="{ 'background': store.dark ? rgbaBind(darkPackColor(pack.difficulty), 0.2) : rgbaBind(lightPackColor(pack.difficulty), 0.3), 'display': !pack.levels ? 'none' : 'inherit' }">{{ pack.name }}</div>
                    </div>
                    <LevelAuthors :author="level.author" :creators="level.creators" :verifier="level.verifier"></LevelAuthors>
                    <h3>Difficulty: {{["Beginner", "Easy", "Medium", "Hard", "Insane", "Mythical", "Extreme", "Supreme", "Ethereal", "Legendary", "Silent", "Impossible"][level.difficulty]}} layout</h3>
                    <div v-if="level.showcase" class="tabs">
                        <button class="tab type-label-lg" :class="{selected: !toggledShowcase}" @click="toggledShowcase = false">
                            <span class="type-label-lg">Verification</span>
                        </button>
                        <button class="tab" :class="{selected: toggledShowcase}" @click="toggledShowcase = true">
                            <span class="type-label-lg">Showcase</span>
                        </button>
                    </div>
                    <iframe class="video" id="videoframe" :src="video" frameborder="0"></iframe>
                    <ul class="stats">
                        <li>
                            <div class="type-title-sm">Points</div>
                            <p>{{ score(level.rank, level.difficulty, 100, level.percentToQualify, list) }}</p>
                        </li>
                        <li>
                            <div class="type-title-sm">ID</div>
                            <p>{{ level.id }}</p>
                        </li>
                        <li>
                            <div class="type-title-sm">Password</div>
                            <p>{{ level.password || 'Free to Copy' }}</p>
                        </li>
                        <li>
                            <div class="type-title-sm">Enjoyment</div>
                            <p>{{ averageEnjoyment(level.records) }}/10</p>
                        </li>
                    </ul>
                    <ul class="stats">
                        <li>
                            <div class="type-title-sm">Song</div>
                            <p><a target="_blank" :href="(level.songLink===undefined)?'#':level.songLink" :style="{'text-decoration':(level.songLink===undefined)?'none':'underline'}">{{ level.song || 'insert here' }}</a></p>
                        </li>
                    </ul>
                    <h2>Records ({{ level.records.length }})</h2>
                    <p><strong>{{ (level.difficulty>3)?level.percentToQualify:100 }}%</strong> or better to qualify</p>
                    <table class="records">
                        <tr v-for="record in level.records" class="record">
                            <td class="percent">
                                <p>{{ record.percent }}%</p>
                            </td>
                            <td class="user">
                                <a :href="record.link" target="_blank" class="type-label-lg">{{ record.user }}</a>
                            </td>
                            <td class="enjoyment">
                                <p v-if="record.enjoyment === undefined">?/10</p>
                                <p v-else>{{ record.enjoyment }}/10</p>
                            </td>
                            <td class="mobile">
                                <img v-if="record.mobile" :src="'/assets/phone-landscape' + (store.dark ? '-dark' : '') + '.svg'" alt="Mobile">

                            </td>
                            <td class="hz">
                                <p>{{ record.hz }}FPS</p>
                            </td>
                        </tr>
                    </table>
                </div>
                <div v-else-if="level.id==0" class="level" style="height: 100%; justify-content: center; align-items: center;">
                    <h1>{{ level.name }}</h1>
                    <h2 style="padding:1rem;">Total Score: {{ localize(fetchTotalScore(list, level.difficulty)) }}</h2> 
                    <table class="records">
                        <tr class="record">
                            <td><h3 class="tier-info tier-info-header">Highest enjoyment: </h3></td>
                            <td><h3 class="tier-info">{{ fetchHighestEnjoyment(list, level.difficulty) }}</h3></td>
                        </tr> 
                        <tr class="record">
                            <td><h3 class="tier-info tier-info-header">Lowest enjoyment: </h3></td>
                            <td><h3 class="tier-info">{{ fetchLowestEnjoyment(list, level.difficulty) }}</h3></td>
                        </tr>
                    </table>
                    <p style="padding-top:1.5rem">The levels below are {{ level.name.replace("(", "").replace(")", "") }}.</p>
                </div>
                <div v-else class="level" style="height: 100%; justify-content: center; align-items: center;">
                    <p>(ノಠ益ಠ)ノ彡┻━┻</p>
                </div>
            </div>
            <div class="meta-container">
                <div class="meta">
                    <div class="errors" v-show="errors.length > 0">
                        <p class="error" v-for="error of errors">{{ error }}</p>
                    </div>
                    <div class="og">
                        <p class="type-label-md">Some of website layout made by <a href="https://tsl.pages.dev/" target="_blank">The Shitty List</a>, Layout List originally created by DJ JDK & Blathers.</p>
                    </div>
                    <hr width="100%" color = black size="4">
                    <template v-if="staff">
                        <h3>List Staff</h3>
                        <ol class="staff">
                            <li v-for="editor in staff">
                                <img :src="'/assets/' + roleIconMap[editor.role] + (store.dark ? '-dark' : '') + '.svg'" :alt="editor.role">
                                <a v-if="editor.link" class="type-label-lg link" target="_blank" :href="editor.link">{{ editor.name }}</a>
                                <p v-else>{{ editor.name }}</p>
                            </li>
                        </ol>
                    </template>
                    <hr width="100%" color = black size="4">
                    <h3>Tags</h3>
                    <p>
                        (⭐ Rated )
                        (✨ Subject to Exemptions )
                        (💫 Accepted Under Old Standards )
                        (🎖️ Creator Contest Winner)
                        (❌ Pending Removal )
                    </p>
                    <hr width="100%" color = black size="4">
                    <h3>Record Submission Requirements</h3>
                    <div class="record-guidelines">
                        <p>
                            You must have achieved the record without using hacks (including hacks that change the physics of the game, ie. physics bypass via MegaHack, however, "Click Between Frames" is allowed).
                        </p>
                        <p>
                            You must have achieved the record on the level that is listed on the site or on an approved bugfixed copy - please check the level ID before you submit a record!
                        </p>
                        <p>
                            Records for Easy+ completions must have clicks or visual tap indication (source audio is acceptable for iPhone users). Edited audio does not count.
                        </p>
                        <p>
                            Complete raw footage is required alongside your record for any layouts in Extreme Tier or above.
                        </p>
                        <p>
                            The recording must have a previous attempt and death animation shown before the completion, unless the completion is on the first attempt.
                        </p>
                        <p>
                            The recording must show the player hit the end-wall as well as present your end stats, or the completion will be invalidated.
                        </p>
                        <p>
                            Do not use secret routes, skips, or bug routes!
                        </p>
                        <p>
                            Cheat Indicator is required for all completions via Geode, MegaHack, or iCreate Pro. If you do not have Cheat Indicator on, your record will likely be invalidated (this is not 100% required for mobile as of yet due to mobile limitations).
                        </p>
                    </div>
                    <hr width="100%" color = black size="4">
                    <h3>Difficulty Rankings</h3>
                    <p>
                        Impossible Layout = Top Extreme Demons (401 to 750 Points)
                    </p>
                    <p>
                        Legendary Layout = Mid Extreme Demons (201 to 400 Points)
                    </p>
                    <p>
                        Extreme Layout = Beginner Extreme Demons (101 to 200 Points)
                    </p>
                    <p>
                        Mythical Layout = High Insane Demons (71 to 100 Points)
                    </p>
                    <p>
                        Insane Layout = Insane Demons (41 to 70 Points)
                    </p>
                    <p>
                        Hard Layout = Hard Demons (21 to 40 Points)
                    </p>
                    <p>
                        Medium Layout = Medium Demons (11 to 20 Points)
                    </p>
                    <p>
                        Easy Layout = Easy Demons (6 to 10 Points)
                    </p>
                    <p>
                        Beginner Layout = Non Demons (1 to 5 Points)
                    </p>
                    <hr width="100%" color = black size="4">
                    <p>
                        For your convenience, the Layout List caches the data for the list in your browser.
                    </p>
                    <p>
                        By using the site, you agree to the storage of this data in your browser. 
                        You can disable this in your browser's settings (turn off local storage), however this will cause 
                        the site to load very slowly and is not recommended.
                    </p>
                    <p>
                        No data specific to you is collected or shared, and you can <u><a target="_blank" href="https://github.com/layout-list/layout-list/">view the site's source code here</a></u>.
                    </p>
                </div>
            </div>
        </main>
    `,

    data: () => ({
        loading: true,
        list: [],
        listlevels: 0,
        staff: [],
        errors: [],
        selected: 0,
        toggledShowcase: false,
        roleIconMap,
        store,
    }),

    methods: {
        embed,
        score,
        averageEnjoyment,
        rgbaBind,
        lightPackColor,
        darkPackColor,
        fetchHighestEnjoyment,
        fetchLowestEnjoyment,
        fetchTotalScore,
        fetchTierLength,
        localize,
    },

    computed: {
        level() {
            return this.list && this.list[this.selected] && this.list[this.selected][2];
        },
        video() {
            if (!this.level.showcase) {
                return embed(this.level.verification);
            }

            return embed(
                this.toggledShowcase
                    ? this.level.showcase
                    : this.level.verification
            );
        },
    },

    async mounted() {
        // Fetch list from store
        this.list = this.store.list;
        this.staff = await fetchStaff();

        // Error handling
        if (!this.list) {
            this.errors = [
                'Failed to load list. Retry in a few minutes or notify list staff.',
            ];
        } else {
            this.store.errors.forEach((err) => 
                this.errors.push(`Failed to load level. (${err}.json)`))

            if (!this.staff) {
                this.errors.push('Failed to load list staff.');
            }
        }

        // Hide loading spinner
        this.loading = false;

        // tests for incorrect difficulties
        let max = fetchTierMinimum(this.list, 0)
        let i = 0
        let currentdiff, newdiff;
        while (i < max) {
            if (this.list[i][2]) {
                let templevel = this.list[i][2]

                newdiff = templevel.difficulty 
                if (templevel.id === 0) {
                    currentdiff = templevel.difficulty
                }
                
                if (newdiff !== currentdiff) console.warn(`Found incorrect difficulty! ${templevel.name} (${templevel.path}.json) is set to ${newdiff}, please set it to ${currentdiff}.`)
            }
            i++
        }
    },

    watch: {        
        store: {
            handler(updated) {
                this.list = updated.list
                updated.errors.forEach(err => {
                    this.errors.push(`Failed to load level. (${err}.json)`);
                })
            }, 
            deep: true
        }
    },
};