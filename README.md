
# 1. Requirements
**1.1 Node.js**
**1.2. Python**

**Node.js** is an open-source, cross-platform, back-end **JavaScript runtime environment** that **runs on a JavaScript Engine (i.e. V8 engine**) and **executes JavaScript code outside a web browser**, which was designed to build scalable network applications

## 1.1 Node.js
### 1.1.1 Install and configure a nvm
We will install **node.js using** a **Node Version Manager (NVM)**. For windows we will use **nvm-windows**.

**Download and install the latest version (1.1.9 atm)** from **[nvm-windows-releases](https://github.com/coreybutler/nvm-windows/releases) (.exe)**.

**After installing** we will **configure the proxy**.
 **Open** a **command prompt** in **administrator mode** and **run `nvm proxy http://example.com:port`**.

### 1.1.2 Install node.js using nvm
**Open** a **command prompt** in **administrator mode** and **run `nvm install latest`**.
This will **install** the **latest version of node** **(v19.0.0 atm)**.

**After installing run `nvm use latest`**


**If**  this **command** **does not work** you can **try this:**

 - Open IE (Chrome did not work for me).
 - Hit the URL `http://registry.npmjs.org`
 - it will download json output if successful.
 - **Now go back to command prompt and try npm install**.
From [https://stackoverflow.com/questions/19824517/get-node-js-npm-command-to-work-behind-corporate-proxy](https://stackoverflow.com/questions/19824517/get-node-js-npm-command-to-work-behind-corporate-proxy).
 


### 1.1.3. Configure npm
**Npm (Node Package Manager)**

**Configure proxy**

Open **`.npmrc`(this is file name not an extension and is usually found in  **`C:\Users\user`** or  **`C:\Users\user\AppData\Roaming\nvm\v19.0.0\node_modules\npm`**) and add the **following lines**: 

`registry=http://registry.npmjs.org`

`proxy=http://example.com:port`

`https-proxy=http://example.com:port`

`http-proxy=http://example.com:port`

`strict-ssl=true`

**Npm** will **install packages automatically** from **`package.json`** file. 
In a **command prompt** navigate to the **`frontend-vue/frontend` folder** and **run `npm install`**.

**If **`npm install`** fails try the following method for proxy configuration:**

`npm config set proxy http://username:password@host:port`

`npm config set https-proxy http://username:password@host:port`

**Or you can edit directly your `~/.npmrc` file:**

`proxy=http://username:password@host:port`

`https-proxy=http://username:password@host:port`

`https_proxy=http://username:password@host:port`

### 1.2. Configure python
**All the required packages are found in `\slyrak` in `requirements.txt` file.**


# 2. Run
Open a command prompt and go to **`\slyrak\frontend-vue\frontend`** then paste the following line
**`npm run dev`**. This should start the **node.js server**. Connect to the shown adress usually **`http://localhost:5173/.`**


# 3. Build
Open a command prompt and go to **`\slyrak\frontend-vue\frontend`** then paste the following line
**`npm run build`**. This should bundle the aplication into the following folder **`\slyrak\frontend-vue\frontend\dist`**

**This are the files that we are going to serve from our flask server.**

# 4. Visual code
**Visual code must have extensions:**

 - ESLint
 - Volar

# 5. Python` backend-fastapi branch`

**To start the project with fastAPI we can use the terminal.**

- Go to terminal tab in PyCharm
- Cd to `\slyrak\backend-flask`
- Run the following line `uvicorn main:app --reload`


# 99. Why
[](https://stackoverflow.com/posts/68333269/timeline)

You don't _have_ to install and use Node to make frontend applications, but it can help a lot, especially in large projects. The main reason it's used is so that script-writers can easily install, use, and update external packages via NPM. For a few examples:

-   Webpack, to consolidate multiple script files into a single one for production (and to minify, if desired)
-   Babel, to automatically transpile scripts written in modern syntax down to ES6 or ES5
-   A linter like ESLint to avoid accidental bugs and enforce a consistent code style
-   A CSS preprocessor for Sass that can turn (concise) Sass into standard (more verbose) CSS consumable by browsers

And so on. Organizing an environment for these sorts of things would be very difficult without NPM (which depends on Node).

None if it is _necessary_, but many find that it can make the development process much easier.

In the process of creating files for the client to consume, if you want to do anything more elaborate than write plain raw `.js`, `.html`, `.css` files, you'll need something extra - which is most often done via NPM.



