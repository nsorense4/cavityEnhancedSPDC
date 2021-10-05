clear; clc; close all; 

cross1 = readNPY("0223_cross_correlation_data_channel1.npy");
cross2 = readNPY("0223_cross_correlation_data_channel2.npy");
g2_1 = readNPY("0222_g2_data_2hr_6meas_1000window.npy");
g2_2 = readNPY("0223_g2_data_3hr_7meas_1000window.npy");
g2_3 = readNPY("0224_g2_data_1hr_7meas_800window_1500iterant.npy");

g2_1_array = g2_1(:,1).*g2_1(:,4)./(g2_1(:,2).*g2_1(:,3));
g2_2_array = g2_2(:,1).*g2_2(:,4)./(g2_2(:,2).*g2_2(:,3));
g2_3_array = g2_3(:,1).*g2_3(:,4)./(g2_3(:,2).*g2_3(:,3));
g2_1_array(:,2) = [-3;-2;-1;0;1;2];
g2_2_array(:,2) = [-3;-2;-1;0;1;2;3];
g2_3_array(:,2) = [-4.5,-3,-1.5,0,1.5,3,4.5]';


figure;
plot(-10:0.1:9.9, cast(cross1,'double')/max(cast(cross1,'double')), 'linewidth', 1.5)
hold on
plot(-10:0.1:9.9, cast(cross2, 'double')/max(cast(cross2, 'double')), 'linewidth', 1.5)
xlabel('$\tau$ [ns]' , 'Interpreter', 'latex', 'fontsize', 16);
ylabel('Normalized Correlation [arb]', 'Interpreter', 'latex', 'fontsize', 18);
ylim([0 1.05])


figure;
plot(g2_1_array(:,2), g2_1_array(:,1))
hold on
plot(g2_2_array(:,2), g2_2_array(:,1))
plot(g2_3_array(:,2), g2_3_array(:,1))
legend
