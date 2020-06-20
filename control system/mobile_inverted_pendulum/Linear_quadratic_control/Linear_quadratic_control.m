% Linear quadratic control 
clear all, close all, clc
m = 2;
M = 5;
b = 0.1;
l = 2;
d = 1;
i = 0.006;
g=9.8;

T=0:0.05:10; %time states

U=0.2*ones(size(T)); %input to the system A unit step input of having duration of 10 and magnitude of 0.2
%Defining the State space model of inverted pendulum
p=i*(M+m) + M*m*l^2;
A=[0 1 0 0;
    0 -(i+m*l^2)*b/p (m^2*g*l^2)/p 0;
    0 0 0 1;
    0 -(m*l*b)/p m*g*l*(M+m)/p 0];
B=[ 0; (i+m*l^2)/p; 0; m*l/p];

%states =poisiton speed theta(in radian) angular speed

%But we only care about "position of cart" and "upright position" of pendulum
%LQR system obviously behave differently if we want different states to
%control  in this case we want to control position of cart and pendulum
C = [1 0 0 0;0 0 1 0];

D=[0;0];
eig(A);
obsv(A,C)

%D = zeros(size(C,1),size(B,2));
sys = ss(A,B,C,D);
%det(gram(sys,'o'))
%%
%LQR SYSTEM
%Can change the penality on position or pendulum 
Q = [1 0 0 0;
    0 1 0 0;
    0 0 1000 0;
    0 0 0 100];
R = 1;
K = lqr(A,B,Q,R);
sys = ss(A-B*K,B,C,D);   %modified state space system

% visualization of the system
tspan = 0:.001:31;
y0 = [3; -0.5; pi+00.5; 0];
[yL,t,xL] = initial(sys,y0,tspan);
[t,yNL] = ode45(@(t,y)cartpend(y,m,M,l,g,d,0),tspan,y0);
%legend(
for k=1:100:length(t)
    drawcartpend_bw(yNL(k,:),m,M,l);
end
figure
plot(t,yNL);
legend('post_cart','speed_cart','postion_pend','angular_speed');