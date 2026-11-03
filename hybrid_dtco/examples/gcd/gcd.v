// SPDX-License-Identifier: Apache-2.0
// Small original Euclidean GCD design for reference-flow integration.
// A request is accepted when start && !busy. Inputs may include zero.
module gcd #(
    parameter WIDTH = 16
) (
    input wire clk,
    input wire reset,
    input wire start,
    input wire [WIDTH-1:0] a_in,
    input wire [WIDTH-1:0] b_in,
    output reg busy,
    output reg done,
    output reg [WIDTH-1:0] result
);
    reg [WIDTH-1:0] a;
    reg [WIDTH-1:0] b;
    always @(posedge clk) begin
        if (reset) begin
            a <= 0;
            b <= 0;
            busy <= 0;
            done <= 0;
            result <= 0;
        end else begin
            done <= 0;
            if (!busy) begin
                if (start) begin
                    a <= a_in;
                    b <= b_in;
                    busy <= 1;
                end
            end else if (a == 0 || b == 0 || a == b) begin
                result <= a == 0 ? b : a;
                busy <= 0;
                done <= 1;
            end else if (a > b) begin
                a <= a - b;
            end else begin
                b <= b - a;
            end
        end
    end
endmodule
