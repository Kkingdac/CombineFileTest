let tag = process.argv[1]
let label = process.argv[2]
let [major, minor, patch] = tag.split('.').map(Number)
const actions = {
    'bug': () => ++patch,
    'enhancement': () => {
        ++minor
        patch = 0
    }
}
actions[label]()
const version = `v${major}.${minor}.${patch}`
process.stdout.write(version)
// core.setOutput("version", version)