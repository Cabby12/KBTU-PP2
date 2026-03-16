def main():
    s = input().strip()
    vowels = "aeiouAEIOU"
    
    if any(char in vowels for char in s):
        print("Yes")
    else:
        print("No")

if __name__ == "__main__":
    main()
