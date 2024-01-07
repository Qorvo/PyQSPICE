// Automatically generated .v file on Sun Dec 31 14:37:36 2023
//

module cntr ( c, o_3_, o_2_, o_1_, o_0_ ) ;
// You will probably want to flush out the nature of these port declarations:
   input reg c;
   output reg o_3_;
   output reg o_2_;
   output reg o_1_;
   output reg o_0_;

   integer cnt;
   // Implement the module here

   initial begin
      cnt = 0;
      {o_3_, o_2_, o_1_, o_0_} = cnt;
   end

   always @ (posedge c) begin
      if(cnt == 15)
         cnt <= 0;
      else
         cnt <= cnt+1;

      {o_3_, o_2_, o_1_, o_0_} = cnt;
   end

endmodule
