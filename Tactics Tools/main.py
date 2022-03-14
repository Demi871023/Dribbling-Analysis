import argparse
import os



if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("-m", "--mode", type=str, help="VT/PJ/TC")
  parser.add_argument("-s", "--source", type=str)
  parser.add_argument("-d", "--desination", type=str)
  
  
  # NOTE : Visualize Trajecotry
  if args.mode == "VT":
    pass
  
  # NOTE : Parser Court Athena .json File
  elif args.mode == "PJ":
    pass
  
  # NOTE : Transfer to Unity Coordinate
  elif args.mode == "TC":
    pass
  
  
  
