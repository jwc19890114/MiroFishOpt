const { spawnSync } = require('child_process');

const run = (cmd, args) => {
  const result = spawnSync(cmd, args, { stdio: 'inherit', shell: true });
  return typeof result.status === 'number' ? result.status : 1;
};

// Best-effort unpause in case containers were paused.
run('docker', ['unpause', 'mirofish-neo4j', 'mirofish-qdrant']);

const status = run('docker', ['compose', '-f', 'docker-compose.local.yml', 'up', '-d']);
process.exit(status);
