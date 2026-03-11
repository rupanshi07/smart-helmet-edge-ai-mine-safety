% Always resolve parent directory
basePath = fileparts(mfilename('fullpath'));

% Go one level up (project root)
projectRoot = fileparts(basePath);

edge = readtable(fullfile(projectRoot, 'results_edge.csv'));
central = readtable(fullfile(projectRoot, 'results_central.csv'));

data = [
    edge.packets_received  central.packets_received;
    edge.events_missed     central.events_missed
];

bar(data)
set(gca, 'XTickLabel', {'Packets Received','Events Missed'})
legend('Edge ML','Central ML')
title('Edge vs Central ML over LoRa')
grid on
